args<-commandArgs(trailingOnly=TRUE)
base<-'/home/boltzmann13/.sci/profiles/generate-sirna/workspace/crispr_design_gene_knockout_001_KIF11_GRCh38'
.libPaths(c(file.path(base,'bootstrap/R-library'),.libPaths()))
suppressPackageStartupMessages(library(crisprScore))
x<-read.csv(args[1],check.names=FALSE,stringsAsFactors=FALSE)
stopifnot(all(nchar(x$guide_sequence)==20),all(nchar(x$off_target_sequence)==20),all(nchar(x$pam)==3))
x$CFD2016<-getCFDScores(spacers=x$guide_sequence,protospacers=x$off_target_sequence,pams=x$pam,nuclease='SpCas9',version='2016')$score
stopifnot(all(is.finite(x$CFD2016)),all(x$CFD2016>=0 & x$CFD2016<=1))
write.csv(x,args[2],row.names=FALSE);cat('CFD_SCORED',nrow(x),'crisprScore',as.character(packageVersion('crisprScore')),'\n')
