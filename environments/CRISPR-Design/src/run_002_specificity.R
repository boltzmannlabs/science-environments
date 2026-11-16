#!/usr/bin/env Rscript
# CRISPR-Design task 002 — stage 2: Bowtie genome-wide off-target + CFD + DRAFT gates + R2/R3 ranking
# Usage: Rscript run_002_specificity.R <run_dir>   (requires stage-1 outputs + built index)
# Policy: off_target_policy v1.0 conventions (NGG, 0-3 mismatches, both strands,
# intended-locus exclusion, bulges NOT_EVALUATED_UNGAPPED_BOWTIE).
args <- commandArgs(trailingOnly=TRUE); stopifnot(length(args)==1)
p <- normalizePath(args[1])
base <- Sys.getenv("CRISPR_PRIOR_BASE")
if (base=="") base <- "/home/boltzmann13/.sci/profiles/generate-sirna/workspace/crispr_design_gene_knockout_001_KIF11_GRCh38"
.libPaths(c(file.path(base,'bootstrap/R-library'),.libPaths()))
suppressPackageStartupMessages({library(crisprScore);library(Biostrings);library(GenomicRanges);library(Rsamtools)})
Sys.setenv(OPENBLAS_NUM_THREADS=1,OMP_NUM_THREADS=1)
BOWTIE <- file.path(base,'bootstrap/runtime/bin/bowtie')
IDX <- file.path(p,'reference/GRCh38.bowtie.idx')
put <- function(x,f) write.csv(x,file.path(p,f),row.names=FALSE,na='')
jwrite <- function(x,f) jsonlite::write_json(x,file.path(p,f),pretty=TRUE,auto_unbox=TRUE,na='null',null='null')
pool <- read.csv(file.path(p,'candidate_pool.csv'),stringsAsFactors=FALSE)
ix <- which(pool$activity_status=='SCORED')
## ---------- Bowtie genome-wide <=3mm search (ungapped) ----------
system2(BOWTIE,c('-a','-v','3','-f',shQuote(file.path(p,'bowtie_queries.fasta')),shQuote(IDX),shQuote(file.path(p,'bowtie_alignments.tsv'))))
raw <- read.delim(file.path(p,'bowtie_alignments.tsv'),header=FALSE,sep='\t',quote='',fill=TRUE,stringsAsFactors=FALSE,colClasses='character')
stopifnot(ncol(raw)>=7); names(raw)[1:7] <- c('candidate_id','strand','chromosome','offset','aligned_query','quality','other_hits')
h <- data.frame(candidate_id=raw$candidate_id,chromosome=raw$chromosome,start=as.integer(raw$offset)+1L,strand=raw$strand,stringsAsFactors=FALSE)
h$end <- h$start+19L
fa <- file.path(p,'reference/GRCh38.primary_assembly.genome.fa'); faf <- FaFile(fa); open(faf)
getseq <- function(chr,s,e,st=rep('+',length(s))){x<-scanFa(faf,GRanges(chr,IRanges(as.integer(s),as.integer(e))));wh<-st=='-';x[wh]<-reverseComplement(x[wh]);as.character(x)}
fai <- scanFaIndex(faf); lens <- setNames(width(fai),as.character(seqnames(fai)))
ps <- ifelse(h$strand=='+',h$end+1L,h$start-3L); pe <- ps+2L
inside <- ps>=1L & pe<=lens[h$chromosome]
h <- h[inside,]; ps <- ps[inside]; pe <- pe[inside]
h$pam <- getseq(h$chromosome,ps,pe,h$strand)
h <- h[grepl('^[ACGT]GG$',h$pam),]; stopifnot(nrow(h)>0)
h$off_target_sequence <- getseq(h$chromosome,h$start,h$end,h$strand)
query <- pool$guide_sequence[match(h$candidate_id,pool$candidate_id)]
qmat <- as.matrix(DNAStringSet(query)); tmat <- as.matrix(DNAStringSet(h$off_target_sequence)); mm <- qmat!=tmat
h$mismatch_count <- rowSums(mm); stopifnot(all(h$mismatch_count<=3))
h$mismatch_positions <- apply(mm,1,function(v) paste(which(v),collapse=';'))
i <- match(h$candidate_id,pool$candidate_id)
h$intended_target <- h$chromosome==pool$chromosome[i] & h$start==pool$start[i] & h$end==pool$end[i] & h$strand==pool$strand[i]
h$CFD_2016 <- getCFDScores(spacers=query,protospacers=h$off_target_sequence,pams=h$pam,nuclease='SpCas9',version='2016')$score
stopifnot(all(is.finite(h$CFD_2016)),all(h$CFD_2016>=0 & h$CFD_2016<=1))
genes <- read.csv(file.path(p,'reference/all_genes.csv'),stringsAsFactors=FALSE)
annotate <- function(tab,field){
 gr<-GRanges(tab$chromosome,IRanges(tab$start,tab$end));hits<-findOverlaps(GRanges(h$chromosome,IRanges(h$start,h$end)),gr,ignore.strand=TRUE)
 vals<-split(tab[[field]][subjectHits(hits)],queryHits(hits))
 vapply(seq_len(nrow(h)),function(k)paste(sort(unique(vals[[as.character(k)]])),collapse=';'),character(1))
}
h$gene_annotation<-annotate(genes,'gene_name');h$gene_annotation[h$gene_annotation=='']<-'INTERGENIC'
h$off_target_id<-sprintf('SITE_%07d',seq_len(nrow(h)))
h$bulge_status<-'NOT_EVALUATED_UNGAPPED_BOWTIE';h$reference_assembly<-'GRCh38.p14';h$index_version<-'Bowtie_1.3.1_GRCh38_primary_rebuilt_Run1'
h$risk_flag<-ifelse(h$intended_target,'INTENDED',ifelse(h$mismatch_count<=2,'HIGH_CONFIDENCE_VETO','THREE_MISMATCH_RISK_FLAG'))
put(h,'off_target_sites.csv')
## ---------- per-guide specificity aggregates ----------
counts <- matrix(NA_integer_,nrow(pool),4,dimnames=list(NULL,paste0('off_target_count_',0:3,'mm')))
spec <- rep(NA_real_,nrow(pool)); intended_count <- rep(NA_integer_,nrow(pool)); cfdburden <- rep(NA_real_,nrow(pool))
for(k in ix){
 z<-h[h$candidate_id==pool$candidate_id[k],];intended_count[k]<-sum(z$intended_target)
 z<-z[!z$intended_target,];counts[k,]<-tabulate(z$mismatch_count+1L,nbins=4)
 cfdburden[k]<-sum(z$CFD_2016);spec[k]<-1/(1+cfdburden[k])
}
pool<-cbind(pool,as.data.frame(counts));pool$specificity_score<-spec;pool$CFD_burden<-cfdburden;pool$intended_hit_count<-intended_count
## ---------- DRAFT gates (v0.1) + brief vetoes: tighten-only ----------
gate <- lapply(seq_len(nrow(pool)),function(k){
 if(pool$activity_status[k]!='SCORED') return(c('NOT_RUN_EXCLUDED_BY_VALIDITY_OR_CODING_SCOPE'))
 reason<-character()
 if(!pool$reference_valid[k]) reason<-c(reason,'REFERENCE_OR_SEQUENCE_INVALID')
 if(!is.na(pool$off_target_count_0mm[k]) && pool$off_target_count_0mm[k]>0) reason<-c(reason,'OFF_TARGET_EXACT_MATCH')
 if(pool$polyT_flag[k]) reason<-c(reason,'POLY_T_TERMINATION_RISK')
 if(is.na(pool$intended_hit_count[k]) || pool$intended_hit_count[k]==0) reason<-c(reason,'INTENDED_LOCUS_NOT_RECOVERED')
 if(length(reason)==0) 'PASS' else reason
})
pool$gate_status<-vapply(gate,function(x)paste(x,collapse=';'),character(1))
gate_log <- data.frame(candidate_id=pool$candidate_id,activity_status=pool$activity_status,
  off_target_count_0mm=pool$off_target_count_0mm,off_target_count_1mm=pool$off_target_count_1mm,
  off_target_count_2mm=pool$off_target_count_2mm,off_target_count_3mm=pool$off_target_count_3mm,
  polyT_flag=pool$polyT_flag,intended_hit_count=pool$intended_hit_count,gate_status=pool$gate_status,stringsAsFactors=FALSE)
put(gate_log,'gate_log.csv')
## ---------- R2 ranking: cohort-percentile preference view (disclosed, never an efficacy estimate) ----------
surv <- which(pool$gate_status=='PASS')
pctrank <- function(v){r<-rank(v,na.last='keep');r/max(r,na.rm=TRUE)}
## preference view only (disclosed): percentile-mean of available on-target endpoints;
## endpoint columns themselves stay separate and are never averaged as efficacy estimates
on_target_pref <- (pctrank(pool$rs1_score)+pctrank(pool$rs3_seq_hsu2013)+pctrank(pool$crisprater_score)+
                     if('crispron_score' %in% names(pool)) pctrank(pool$crispron_score) else 0)/
  (3 + if('crispron_score' %in% names(pool)) 1 else 0)
pool$on_target_preference_view <- on_target_pref
dims <- data.frame(on_target=on_target_pref,specificity=pctrank(pool$specificity_score),
  outcome_quality=pctrank(pool$frameshift_score),context=pctrank(pool$mean_early_CDS))
W <- c(on_target=0.35,specificity=0.25,outcome_quality=0.30,context=0.10)
score <- as.matrix(dims)%*%W
pool$weighted_preference_score <- score
## stability: +-25% deterministic weight perturbations
perturbs <- list(c(0.4375,0.25,0.30,0.10),c(0.2625,0.25,0.30,0.10),c(0.35,0.3125,0.30,0.10),
                 c(0.35,0.25,0.375,0.10),c(0.35,0.25,0.30,0.125))
stab <- sapply(perturbs,function(w){s<-as.matrix(dims[surv,])%*%w;names(s)<-pool$candidate_id[surv];head(names(sort(s,decreasing=TRUE)),6)})
base_top <- head(pool$candidate_id[surv][order(score[surv],decreasing=TRUE)],6)
stab_overlap <- apply(stab,2,function(x)length(intersect(x,base_top)))
## R3 site-distinct panel
ord <- surv[order(score[surv],decreasing=TRUE)]
panel <- character(); used <- IRanges()
for(k in ord){
  rv <- IRanges(pool$start[k],pool$end[k])
  if(length(subjectHits(findOverlaps(rv,used)))>0) next
  panel <- c(panel,pool$candidate_id[k]); used <- c(used,rv)
  if(length(panel)>=6) break
}
shortlist <- pool[match(panel,pool$candidate_id),]
put(pool,'candidate_pool.csv');put(shortlist,'ranked_shortlist.csv')
jwrite(list(run='stage2_specificity_gates_ranking',bowtie_version='1.3.1',index='rebuilt_Run1_GRCh38_primary',
  alignments=nrow(h),guides_searched=length(ix),gate_pass=sum(pool$gate_status=='PASS'),
  panel=panel,panel_stability_top6_overlap=stab_overlap,
  weights=W,thresholds_version='0.1-draft',
  ranking_note='weighted score is a disclosed preference view over percentile-ranked dimensions; on-target endpoints remain separate columns and are never averaged as efficacy estimates',
  intended_locus_missing=sum(pool$intended_hit_count[ix]==0,na.rm=TRUE),
  status='COMPLETED'),'run_record_stage2.json')
cat('STAGE2 DONE: alignments',nrow(h),'| gate_pass',sum(pool$gate_status=='PASS'),'| panel',length(panel),'\n')
