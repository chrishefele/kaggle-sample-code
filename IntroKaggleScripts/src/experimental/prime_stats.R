
print("reading primes")
primes <- scan("primes_multiprocess.csv")
primes <- primes[ 2:length(primes) ]

print(unique(primes %% 6))

p.mod6.plus1 <- primes[primes %% 6 ==  1    ]
p.mod6.plus5 <- primes[primes %% 6 == -1 + 6]

diff.mod6.plus1 <- diff(p.mod6.plus1) %/% 6
diff.mod6.plus5 <- diff(p.mod6.plus5) %/% 6 


entropy.bits  <- function(arr) {
    freqs <- table(arr) / length(arr)
    -sum(freqs * log2(freqs))
}

print(entropy.bits(diff.mod6.plus1))
print(entropy.bits(diff.mod6.plus5))

write.csv(diff.mod6.plus1, file="primes_6n+1.csv", col.names=FALSE, row.names=FALSE)
write.csv(diff.mod6.plus5, file="primes_6n-1.csv", col.names=FALSE, row.names=FALSE)


