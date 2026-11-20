"""Additive, auditable local inference helpers; upstream sources/checkpoints remain unchanged.
Strict site validation prevents the upstream find==-1 path from inventing flank features.
Batching is checked against native single-row inference; no efficacy endpoints are averaged.
"""
import pathlib,sys,time,math
import numpy as np
BASE=pathlib.Path('/home/boltzmann13/IMRAN/OCT26/siRNA-Bench')
sys.path.insert(0,str(BASE/'src'))
from sirna_bench.adapters.efficacy import RnAiPredictAdapter,RnAiSplineAdapter

def rc(s):return s.translate(str.maketrans('AUCG','UAGC'))[::-1]
def validate_pair(guide,context,allow_unknown_flanks=False):
 if not 19<=len(guide)<=21 or set(guide)-set('AUCG'):raise ValueError('Require an explicitly derived 19-21 nt RNA guide')
 if set(context)-set('AUCGN'):raise ValueError('Invalid context alphabet')
 if 'N' in context and not allow_unknown_flanks:raise ValueError('Unknown flanks need explicit degraded-context mode')
 site=rc(guide[:19]);positions=[i for i in range(len(context)-18) if context.startswith(site,i)]
 if not positions:raise ValueError('Exact first-19-nt target site missing; refuse upstream find==-1 tokenization')
 i=positions[0];left=context[max(0,i-19):i];right=context[i+19:i+38]
 real_left=sum(b!='N' for b in left);real_right=sum(b!='N' for b in right)
 return {'site_index_in_context':i,'exact_site_occurrences':len(positions),'real_left_flank_nt':real_left,'real_right_flank_nt':real_right,'context_quality':'FULL_REAL_FLANKS' if real_left==19 and real_right==19 else 'DEGRADED_OR_EDGE_CONTEXT','guide_input_nt':len(guide),'primary_site_core_nt':19}

class AuditedPredictors:
 def __init__(self):self.rnai=None;self.spline=None;self.validation_checks=[]
 def rnai_batch(self,pairs,allow_unknown_flanks=False):
  from Bio.Seq import Seq
  from Bio.SeqRecord import SeqRecord
  audit=[validate_pair(g,c,allow_unknown_flanks) for g,c in pairs]
  if self.rnai is None:self.rnai=RnAiPredictAdapter();self.rnai._ensure()
  ad=self.rnai;sr=[];five=[];three=[]
  for g,c in pairs:
   s=ad._siRNA_cls(SeqRecord(Seq(g),id='validated'))
   m=ad._mRNA_cls(SeqRecord(Seq(c.replace('U','T')),id='validated'))
   f,t=m.nucleotide_tokenization(s,split=True);sr.append(s.nucleotide_tokenization());five.append(f);three.append(t)
  x={str(ad._Feature.SIRNA_TOKEN):np.asarray(sr),str(ad._Feature.MRNA_5_FLANK_TOKEN):np.asarray(five),str(ad._Feature.MRNA_3_FLANK_TOKEN):np.asarray(three)}
  y=ad._model.predict(x,batch_size=64,verbose=0).flatten()
  if not np.isfinite(y).all():raise RuntimeError('Non-finite RN.Ai result')
  scores=[round(float(v)*100,2) for v in y]
  for idx in sorted(set([0,len(pairs)//2,len(pairs)-1])):
   p=ad.predict_pair(*pairs[idx]);native=p.raw_score
   if native is None or abs(native-scores[idx])>.011:raise RuntimeError('Batched inference does not reproduce native single-row inference')
   self.validation_checks.append({'operation':'RN.Ai batch_vs_native','row':idx,'native':native,'batch':scores[idx],'absolute_delta':abs(native-scores[idx])})
  return [{'score':s,'status':'ok',**a} for s,a in zip(scores,audit)]
 def spline_batch(self,pairs):
  audit=[validate_pair(g,c) for g,c in pairs]
  if any('N' in c for _,c in pairs):raise ValueError('RNAiSpline does not support synthetic N flanks')
  if self.spline is None:self.spline=RnAiSplineAdapter()
  result=[]
  for (g,c),a in zip(pairs,audit):
   p=self.spline.predict_pair(g,c)
   if p.raw_score is None or not math.isfinite(p.raw_score):raise RuntimeError('RNAiSpline inference failed: '+str(p.provenance))
   result.append({'score':float(p.raw_score),'status':'ok',**a})
  return result
