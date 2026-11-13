args<-commandArgs(trailingOnly=TRUE);root<-args[1]
base<-'/home/boltzmann13/.sci/profiles/generate-sirna/workspace/crispr_design_gene_knockout_001_KIF11_GRCh38'
.libPaths(c(file.path(base,'bootstrap/R-library'),.libPaths()))
suppressPackageStartupMessages(library(randomForest));dir.create(file.path(root,'predictions','cas13'),showWarnings=FALSE)
x<-read.csv(file.path(root,'data/cas13_feature_table.csv'),check.names=FALSE)
f<-c('MFE','DR','Gquad','Log10_Unpaired','hybMFE_3.12','hybMFE_15.9','NTdens_max_A','NTdens_max_C','NTdens_max_G','NTdens_max_T','NTdens_max_AT','NTdens_max_GC','NTdens_min_A','NTdens_min_C','NTdens_min_G','NTdens_min_T','NTdens_min_AT','pA','pC','pG','pAA','pAC','pAG','pAT','pCA','pCC','pCG','pCT','pGA','pGC','pGG','pGT','pTA','pTC','pTG')
stopifnot(length(f)==35,all(f %in% names(x)),nrow(x)==2918,all(complete.cases(x[,c(f,'normCS','Screen')])))
# Published feature table/response and published percentile clipping; no fitted final model reused.
X<-x[,f];numeric<-sapply(X,is.numeric) & !names(X)%in%c('DR','Gquad') & !grepl('[A,C,G,T]_',names(X))
low<-sapply(X[,numeric],quantile,probs=.05);hi<-sapply(X[,numeric],quantile,probs=.95);stopifnot(all(hi>low))
X[,numeric]<-sweep(sweep(X[,numeric],2,low,'-'),2,hi-low,'/');X[,numeric][X[,numeric]<0]<-0;X[,numeric][X[,numeric]>1]<-1
y<-x$normCS;set.seed(20261111);train<-unlist(lapply(split(seq_len(nrow(x)),x$Screen),function(i)sample(i,floor(.7*length(i)))))
test<-setdiff(seq_len(nrow(x)),train);stopifnot(!length(intersect(train,test)))
split<-data.frame(row=seq_len(nrow(x)),screen=x$Screen,GuideName=x$GuideName,partition=ifelse(seq_len(nrow(x))%in%train,'train','test'))
write.csv(split,file.path(root,'data/cas13_probe_split.csv'),row.names=FALSE)
start<-proc.time()[3];m<-randomForest(x=X[train,],y=y[train],ntree=2000,mtry=12)
p<-predict(m,X[test,]);secs<-proc.time()[3]-start
out<-data.frame(row=test,screen=x$Screen[test],truth=y[test],prediction=p);write.csv(out,file.path(root,'predictions/cas13/probe_heldout_predictions.csv'),row.names=FALSE)
saveRDS(list(features=f,low=low,high=hi,numeric=numeric),file.path(root,'protocols/cas13_feature_preprocessing.rds'))
cat('RF_TIMING_SECONDS',secs,'NTRAIN',length(train),'NTEST',length(test),'SPEARMAN',cor(y[test],p,method='spearman'),'\n')
cat('SCREENS',paste(names(table(x$Screen)),table(x$Screen),collapse=';'),'\n');cat('R',R.version.string,'randomForest',as.character(packageVersion('randomForest')),'\n')
