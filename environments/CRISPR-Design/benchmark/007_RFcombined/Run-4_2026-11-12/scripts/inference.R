args<-commandArgs(trailingOnly=TRUE);root<-normalizePath(args[1]);workers<-as.integer(args[2]);stopifnot(workers>=1,workers<=2)
base<-'/home/boltzmann13/.sci/profiles/generate-sirna/workspace/crispr_design_gene_knockout_001_KIF11_GRCh38'
.libPaths(c(file.path(base,'bootstrap/R-library'),.libPaths()))
suppressPackageStartupMessages({library(randomForest);library(jsonlite)})
out<-file.path(root,'predictions','cas13_RFcombined_source_audited_v2');dir.create(out,recursive=TRUE,showWarnings=FALSE)
x<-read.csv(file.path(root,'data/cas13_feature_table.author_order.csv'),check.names=FALSE)
f<-c('MFE','DR','Gquad','Log10_Unpaired','hybMFE_3.12','hybMFE_15.9','NTdens_max_A','NTdens_max_C','NTdens_max_G','NTdens_max_T','NTdens_max_AT','NTdens_max_GC','NTdens_min_A','NTdens_min_C','NTdens_min_G','NTdens_min_T','NTdens_min_AT','pA','pC','pG','pAA','pAC','pAG','pAT','pCA','pCC','pCG','pCT','pGA','pGC','pGG','pGT','pTA','pTC','pTG')
stopifnot(nrow(x)==2918,length(f)==35,all(complete.cases(x[,c(f,'normCS','Screen')])))
X<-x[,f];continuous<-sapply(X,is.numeric)&!names(X)%in%c('DR','Gquad')&!grepl('[A,C,G,T]_',names(X));y<-x$normCS
scale_train_test<-function(tr,te){lo<-sapply(X[tr,continuous],quantile,probs=.05);hi<-sapply(X[tr,continuous],quantile,probs=.95);stopifnot(all(hi>lo));a<-X[tr,];b<-X[te,];a[,continuous]<-sweep(sweep(a[,continuous],2,lo,'-'),2,hi-lo,'/');b[,continuous]<-sweep(sweep(b[,continuous],2,lo,'-'),2,hi-lo,'/');a[,continuous][a[,continuous]<0]<-0;a[,continuous][a[,continuous]>1]<-1;b[,continuous][b[,continuous]<0]<-0;b[,continuous][b[,continuous]>1]<-1;list(train=a,test=b)}
# Source prepare_datasets.R used R3.5 and set.seed(1234); reproduce its pre-R3.6 sampling kind.
RNGversion('3.5.0');set.seed(1234);source_seeds<-sample(1:10000,1000,replace=FALSE)
write.csv(data.frame(replicate=0:999,source_seed=source_seeds),file.path(root,'protocols/cas13_recovered_seed_schedule.csv'),row.names=FALSE)
protocol<-list(model='RFcombined',paper='10.1038/s41587-020-0456-9',features=f,n=2918,ntree=2000,mtry=12,replicates=1000,workers=workers,seed_base=20261111,
 split='Original source seed schedule set.seed1234 sample1..10000 (R3.5 sampling kind) and source-ordered rows; screen-balanced 70/30 disjoint row splits. RF model seeds are explicitly fixed because original comparative fitting script did not fix them.',
 preprocessing='Original source-ordered published 35-feature matrix and normCS labels; training-set-only 5th/95th percentile clipping; no all-data RF used as held-out predictor; global published feature selection/label normalization inherited.',
 source_parameter_discrepancy='Paper final model:2000 trees,mtry12; comparative source:randomForest defaults; final CV source:mtry10. This run retains requested2000/mtry12 paper parameters. It is a qualified protocol reimplementation, not an exact replay of every code variant.',
 interpretation='1000 refit/resplit distribution; percentile intervals describe split/refit variability, not a model-free CI for a new target population',
 r_version=R.version.string,randomForest_version=as.character(packageVersion('randomForest')))
write_json(protocol,file.path(root,'protocols/cas13_RFcombined.json'),auto_unbox=TRUE,pretty=TRUE)
fit_one<-function(rep){
 p<-file.path(out,sprintf('replicate_%04d.json',rep));if(file.exists(p))return(read_json(p,simplifyVector=TRUE))
 seed<-source_seeds[rep+1L];set.seed(seed);strata<-split(seq_len(nrow(x)),x$Screen);selection<-lapply(strata,function(i)sample(seq_along(i),.7*length(i),replace=FALSE));tr<-unlist(Map(function(i,j)i[j],strata,selection),use.names=FALSE);te<-unlist(Map(function(i,j)i[-j],strata,selection),use.names=FALSE);stopifnot(!length(intersect(tr,te)))
 scaled<-scale_train_test(tr,te);set.seed(20261111L+rep)
 t0<-proc.time()[3];m<-randomForest(x=scaled$train,y=y[tr],ntree=2000,mtry=12);pred<-predict(m,scaled$test);stopifnot(all(is.finite(pred)))
 fcsv<-file.path(out,sprintf('replicate_%04d_predictions.csv.gz',rep));con<-gzfile(fcsv,'wt');write.csv(data.frame(row=te,screen=x$Screen[te],truth=y[te],prediction=pred),con,row.names=FALSE);close(con)
 partition<-file.path(out,sprintf('replicate_%04d_partition.csv.gz',rep));con<-gzfile(partition,'wt');write.csv(data.frame(row=seq_len(nrow(x)),screen=x$Screen,partition=ifelse(seq_len(nrow(x))%in%tr,'train','test')),con,row.names=FALSE);close(con)
 r<-list(replicate=rep,seed=seed,n_train=length(tr),n_test=length(te),spearman=unname(cor(y[te],pred,method='spearman')),pearson_squared=unname(cor(y[te],pred)^2),MSE=mean((y[te]-pred)^2),seconds=unname(proc.time()[3]-t0),train_test_overlap=0)
 write_json(r,p,auto_unbox=TRUE,pretty=TRUE);if(rep%%20==0){cat('COMPLETED_REPLICATE',rep,'SPEARMAN',r$spearman,'\n');flush.console()};r
}
cat('STARTING_1000_RF_FITS',format(Sys.time(),tz='UTC'),'workers',workers,'\n');flush.console()
res<-parallel::mclapply(0:999,fit_one,mc.cores=workers,mc.preschedule=FALSE,mc.set.seed=FALSE)
if(any(vapply(res,inherits,logical(1),'try-error')))stop('One or more training workers failed; inspect individual records')
tab<-do.call(rbind,lapply(res,as.data.frame));write.csv(tab,file.path(root,'reports/cas13_RFcombined_1000_resampling_metrics.csv'),row.names=FALSE)
# Independent model-family generalization check: retrain with each entire screen held out.
loso<-lapply(sort(unique(x$Screen)),function(screen){
 tr<-which(x$Screen!=screen);te<-which(x$Screen==screen);scaled<-scale_train_test(tr,te);set.seed(20261111L+match(screen,sort(unique(x$Screen))));m<-randomForest(x=scaled$train,y=y[tr],ntree=2000,mtry=12);p<-predict(m,scaled$test);
 write.csv(data.frame(row=te,screen=screen,truth=y[te],prediction=p),file.path(out,paste0('LOSO_',screen,'.csv')),row.names=FALSE)
 data.frame(screen=screen,n=length(te),spearman=cor(y[te],p,method='spearman'),pearson_squared=cor(y[te],p)^2,MSE=mean((y[te]-p)^2))})
loso<-do.call(rbind,loso);write.csv(loso,file.path(root,'reports/cas13_RFcombined_leave_screen_out.csv'),row.names=FALSE)
summary<-list(status='COMPLETED_PROTOCOL_REIMPLEMENTATION',replicates=nrow(tab),median_spearman=median(tab$spearman),mean_spearman=mean(tab$spearman),split_refit_percentile_interval=unname(quantile(tab$spearman,c(.025,.975))),median_pearson_squared=median(tab$pearson_squared),paper_reported_spearman_approx=.67,qualification='Recovered source split seeds with legacy R3.5 sampling; per-training-split scaling corrected. Paper2000/mtry12 parameters retained, whereas comparative source uses RF defaults and final-CV source usesmtry10; no claim of exact replay of all source variants or raw-feature reconstruction',LOSO=loso)
write_json(summary,file.path(root,'reports/cas13_RFcombined_verified_summary.json'),auto_unbox=TRUE,pretty=TRUE)
cat('ALL_1000_AND_LOSO_COMPLETED\n');print(summary)
