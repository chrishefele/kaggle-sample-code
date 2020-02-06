
meanfreq <- function(x) {
    full.pwr.spectrum <- Mod( fft(x) )^2
    first.half.freqs <- 1:(length(full.pwr.spectrum)/2)
    pwr.spectrum <- full.pwr.spectrum[ first.half.freqs ]  
    mean.freq <- sum( pwr.spectrum*(first.half.freqs-1) ) / sum( pwr.spectrum ) 
    return( mean.freq ) 
}

