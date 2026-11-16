#!/usr/bin/env Rscript
# CRISPR-Design task 002 (knockout) — stage 1: enumerate + validate + on-target + indel + physico-chem
# Usage: Rscript run_002_knockout.R <run_dir>
# Endpoints (separate columns, native units, never averaged):
#   RuleSet1 (30nt), RuleSet3-Sequence Hsu2013 (30nt, python env), CRISPRater (20nt),
#   CRISPRscan (35nt, T7/IVT context column), Lindel frameshift (65nt).
# Conventions inherited verbatim from the verified prior KIF11 run (off_target_policy v1.0).
args <- commandArgs(trailingOnly=TRUE); stopifnot(length(args)==1)
p <- normalizePath(args[1])
base <- Sys.getenv("CRISPR_PRIOR_BASE")
if (base=="") base <- "/home/boltzmann13/.sci/profiles/generate-sirna/workspace/crispr_design_gene_knockout_001_KIF11_GRCh38"
.libPaths(c(file.path(base,'bootstrap/R-library'),.libPaths()))
RS3_ENV <- '/home/boltzmann13/IMRAN/NOV26/cirspr-sci-env/03_environment/rs3-env'
LINDEL_ENV <- file.path(base,'runs/20261105T102927Z/lindel-runtime')
suppressPackageStartupMessages({library(crisprDesign);library(crisprScore);library(crisprBase);library(Biostrings);library(GenomicRanges);library(Rsamtools)})
options(timeout=600); Sys.setenv(OPENBLAS_NUM_THREADS=1,OMP_NUM_THREADS=1)
put <- function(x,f) write.csv(x,file.path(p,f),row.names=FALSE,na='')
jwrite <- function(x,f) jsonlite::write_json(x,file.path(p,f),pretty=TRUE,auto_unbox=TRUE,na='null',null='null')
fa <- file.path(p,'reference/GRCh38.primary_assembly.genome.fa')
if(!file.exists(paste0(fa,'.fai'))) Rsamtools::indexFa(fa)
faf <- FaFile(fa); open(faf)
getseq <- function(chr,s,e,st=rep('+',length(s))) {
 x <- scanFa(faf,GRanges(chr,IRanges(as.integer(s),as.integer(e))))
 wh <- st=='-'; x[wh] <- reverseComplement(x[wh]); as.character(x)
}
## ---------- reference validation (prior-run recipe, trimmed assert set) ----------
a <- read.csv(file.path(p,'reference/target_annotation.csv'),stringsAsFactors=FALSE)
pcs <- a$transcript_id[a$feature=='transcript' & a$transcript_type=='protein_coding']; pcs <- sort(unique(pcs))
gene <- a[a$feature=='gene',]; stopifnot(nrow(gene)==1, gene$gene_name=='KIF11')
## ---------- enumerate canonical NGG windows across locus (both strands) ----------
region_start <- gene$start-100L; region_end <- gene$end+100L
sequence <- getseq(gene$chromosome,region_start,region_end)
data(SpCas9,package='crisprBase')
gs <- findSpacers(setNames(sequence,gene$chromosome),crisprNuclease=SpCas9,canonical=TRUE,both_strands=TRUE,remove_ambiguities=FALSE)
strand <- as.character(strand(gs)); pam_site <- as.integer(pamSites(gs))+region_start-1L
s <- ifelse(strand=='+',pam_site-20L,pam_site+1L); e <- s+19L
cut <- as.integer(cutSites(gs))+region_start-1L
pool <- data.frame(candidate_id=sprintf('KIF11_%05d',seq_along(gs)),
  guide_sequence=as.character(spacers(gs)),pam=as.character(pams(gs)),
  genome_assembly='GRCh38.p14',chromosome=gene$chromosome,start=s,end=e,strand=strand,
  pam_site=pam_site,cut_site=cut,target_gene='KIF11',stringsAsFactors=FALSE)
## E1 validation: alphabet, reference round-trip
valid <- grepl('^[ACGT]{20}$',pool$guide_sequence) & grepl('^[ACGT]GG$',pool$pam)
ref_spacer <- getseq(pool$chromosome,s,e,strand)
ref_pam <- getseq(pool$chromosome,ifelse(strand=='+',e+1L,s-3L),ifelse(strand=='+',e+3L,s-1L),strand)
valid <- valid & ref_spacer==pool$guide_sequence & ref_pam==pool$pam
pool$reference_valid <- valid
## coding coverage (cut site in CDS of each protein-coding transcript)
cds <- a[a$feature=='CDS' & a$transcript_id %in% pcs,]
coverage<-list(); covmatrix<-matrix(FALSE,nrow(pool),length(pcs),dimnames=list(NULL,pcs)); early<-matrix(NA_real_,nrow(pool),length(pcs))
for(j in seq_along(pcs)){
 tx<-pcs[j]; ex<-cds[cds$transcript_id==tx,]; ex<-ex[order(ex$start),]; total<-sum(ex$end-ex$start+1)
 cumulative<-c(0,cumsum(ex$end-ex$start+1))
 ## annotation CSV has exon_id but no exon_number column — synthesize exon_index in genomic order
 ex$exon_index <- seq_len(nrow(ex))
 for(k in seq_len(nrow(ex))){
  hit<-which(cut>=ex$start[k] & cut<=ex$end[k]); if(!length(hit)) next
  covmatrix[hit,j]<-TRUE
  pos<-cumulative[k]+cut[hit]-ex$start[k]+1
  early[hit,j]<-1-pos/total
  coverage[[length(coverage)+1L]]<-data.frame(candidate_id=pool$candidate_id[hit],transcript_id=tx,exon_id=ex$exon_id[k],exon_index=ex$exon_index[k],CDS_cut_position=pos,CDS_length=total,CDS_cut_fraction=pos/total)
 }
}
cov<-do.call(rbind,coverage); put(cov,'transcript_coverage.csv')
pool$covered_transcript_count<-rowSums(covmatrix); pool$total_transcript_count<-length(pcs)
pool$transcript_coverage<-pool$covered_transcript_count/length(pcs)
pool$target_transcript<-apply(covmatrix,1,function(x) paste(pcs[x],collapse=';'))
exons_by_guide<-split(cov$exon_id,cov$candidate_id)
pool$target_exon<-vapply(pool$candidate_id,function(x) paste(sort(unique(exons_by_guide[[x]])),collapse=';'),character(1))
pool$coding_region_status<-ifelse(pool$covered_transcript_count>0,'CODING_CUT_SITE','OUTSIDE_CODING_SCOPE')
## E6 physico-chem
pool$gc_percent<-100*rowSums(letterFrequency(DNAStringSet(pool$guide_sequence),c('G','C')))/20
pool$homopolymer_flag<-grepl('A{5}|C{5}|G{5}|T{5}',pool$guide_sequence)
pool$polyT_flag<-grepl('TTTT',pool$guide_sequence,fixed=TRUE)
pool$gc_flag_draft_40_80<-pool$gc_percent<40 | pool$gc_percent>80      # DRAFT gate band
pool$gc_flag_prior_30_70<-pool$gc_percent<30 | pool$gc_percent>70      # prior-run band (reported for calibration)
gc_count <- pool$gc_percent/100*20
at_count <- 20-gc_count
pool$tm_wallace_celsius<-2*at_count+4*gc_count                          # method stated: Wallace rule
ix<-which(valid & pool$covered_transcript_count>0)
cat('GENERATED',nrow(pool),'WINDOWS; CODING_VALID',length(ix),'\n')
## ---------- E2 on-target endpoints (separate columns, native units) ----------
## Guide-oriented context windows (strand-aware; same convention as the Lindel context):
##   seq30 [4][20][PAM][3]:  + strand = fwd [start-4, end+6];  - strand = fwd [start-6, end+4] (revcomp)
##   seq35 [6][20][PAM][6]:  + strand = fwd [start-6, end+9];  - strand = fwd [start-9, end+6] (revcomp)
s30 <- ifelse(pool$strand=='+',
              getseq(pool$chromosome,pool$start-4,pool$end+6,'+'),
              getseq(pool$chromosome,pool$start-6,pool$end+4,'-'))
s35 <- ifelse(pool$strand=='+',
              getseq(pool$chromosome,pool$start-6,pool$end+9,'+'),
              getseq(pool$chromosome,pool$start-9,pool$end+6,'-'))
pool$seq30<-s30; pool$seq35<-s35
## coordinate-integrity assertion (scored subset): spacer+PAM at expected offsets of every context window
stopifnot(all(substr(s30[ix],5,24)==pool$guide_sequence[ix]), all(substr(s30[ix],25,27)==pool$pam[ix]),
          all(substr(s35[ix],7,26)==pool$guide_sequence[ix]), all(substr(s35[ix],27,29)==pool$pam[ix]))
pool$rs1_score<-NA_real_; pool$rs3_seq_hsu2013<-NA_real_; pool$crisprater_score<-NA_real_; pool$crisprscan_t7<-NA_real_
stopifnot(all(nchar(s30[ix])==30),all(nchar(s35[ix])==35),all(grepl('GG$',substr(s30[ix],25,27))))
pool$rs1_score[ix] <- getRuleSet1Scores(s30[ix])$score
rs3 <- getRuleSet3Scores(s30[ix], tracrRNA='Hsu2013', condaEnv=RS3_ENV); pool$rs3_seq_hsu2013[ix] <- rs3$score
pool$crisprater_score[ix] <- vapply(pool$guide_sequence[ix], function(x) getCRISPRaterScores(x)$score, numeric(1))
pool$crisprscan_t7[ix] <- getCRISPRscanScores(s35[ix])$score
## ---------- E2e CRISPRon (upstream pipeline, AGPL-3.0 internal-use; TF2.14/Keras2 env) ----------
CRISPRON_PKG <- '/home/boltzmann13/IMRAN/NOV26/cirspr-sci-env/02_benchmarks/datasets/crispron-v1.0/RTH-tools-crispron-c8e430b'
CRISPRON_ENV <- '/home/boltzmann13/IMRAN/NOV26/cirspr-sci-env/03_environment/crispron-env'
pool$crispron_score<-NA_real_
if (dir.exists(file.path(CRISPRON_PKG,'bin')) && file.exists(file.path(CRISPRON_ENV,'bin/python'))) {
  writeXStringSet(DNAStringSet(setNames(s30[ix],pool$candidate_id[ix])),file.path(p,'crispron_input.fa'))
  system2('bash',c(shQuote(file.path(CRISPRON_PKG,'bin/CRISPRon.sh')),shQuote(file.path(p,'crispron_input.fa')),shQuote(file.path(p,'crispron_out'))),
          env=paste0('PATH=',CRISPRON_ENV,'/bin:',Sys.getenv('PATH')))
  cp <- read.csv(file.path(p,'crispron_out/crispron.csv'),stringsAsFactors=FALSE)
  ## CRISPRon enumerates every NGG window per record (IDs get _p_N suffixes): join on the exact 30-mer
  m <- match(s30[ix], cp$X30mer)
  if(is.null(m)) m <- match(s30[ix], cp$`30mer`)
  stopifnot(sum(!is.na(m))>=0.95*length(ix))
  hit <- which(!is.na(m)); pool$crispron_score[ix][hit] <- cp$CRISPRon[m[hit]]
} else {
  cat('CRISPRon backend absent -> crispron_score stays NOT_RUN(backend-absent)\n')
}
## ---------- E4 Lindel frameshift (65nt context: 13+20+3+29) ----------
context <- getseq(pool$chromosome[ix], ifelse(pool$strand[ix]=='+',pool$start[ix]-13,pool$start[ix]-32), ifelse(pool$strand[ix]=='+',pool$end[ix]+32,pool$end[ix]+13), pool$strand[ix])
stopifnot(all(substr(context,14,33)==pool$guide_sequence[ix]), all(substr(context,34,36)==pool$pam[ix]), all(nchar(context)==65))
lindel <- getLindelScores(context, condaEnv=LINDEL_ENV)
stopifnot(all(is.finite(lindel$score)), all(lindel$score>=0 & lindel$score<=1))
pool$frameshift_score<-NA_real_; pool$frameshift_score[ix]<-lindel$score
pool$mean_early_CDS<-rowMeans(early,na.rm=TRUE); pool$mean_early_CDS[is.nan(pool$mean_early_CDS)]<-NA_real_
pool$activity_status<-ifelse(seq_len(nrow(pool)) %in% ix,'SCORED','NOT_RUN_EXCLUDED_BY_VALIDITY_OR_CODING_SCOPE')
pool$evidence_tier<-'NEEDS_EXPERIMENTAL_VALIDATION'
put(pool,'candidate_pool.csv')
## spacers FASTA for Bowtie (coding-valid only) + determinism fixture (fixed first-20 coding-valid)
writeXStringSet(DNAStringSet(setNames(pool$guide_sequence[ix],pool$candidate_id[ix])),file.path(p,'bowtie_queries.fasta'))
writeLines(pool$guide_sequence[ix][1:min(20,length(ix))],file.path(p,'determinism_fixture_spacers.txt'))
jwrite(list(run='stage1_enumerate_and_score',windows_total=nrow(pool),coding_valid=length(ix),
  endpoints=c('RuleSet1','RuleSet3-Sequence-Hsu2013','CRISPRater','CRISPRscan-T7-context','Lindel-frameshift'),
  r_version=paste(R.version$major,R.version$minor,sep='.'),crisprScore=as.character(packageVersion('crisprScore')),
  crisprDesign=as.character(packageVersion('crisprDesign')),rs3_env=RS3_ENV,lindel_env=LINDEL_ENV,
  note='CRISPRscan is a T7/IVT-context endpoint (Haeussler 2016); run context is U6 - reported as context column only',
  status='COMPLETED'), 'run_record_stage1.json')
cat('STAGE1 DONE\n')
