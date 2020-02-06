
cat('\n*** Copying .CSV feature files to compact .Rsave format *** \n\n')

save.df <- function(dframe, fname) { save(dframe, file=fname) }
load.df <- function(        fname) { load(fname); return(dframe) }

file.names <- commandArgs(TRUE)
for(fname in file.names) {

    cat('Reading: ')
    cat(fname)
    cat('\n')
    df <- read.csv(fname)

    new.fname <- paste(fname,'.Rsave',sep='')
    cat('Writing: ')
    cat(new.fname)
    cat('\n')
    save.df(df, new.fname)
    cat('\n')

}


