NUM_PREDICTIONS <- 70942

meansqerr <- function(p,a) { mean((log(p+1)-log(a+1))^2) }

rmsle_vs_dih <- read.csv("rmsle_vs_dih.csv")
rmsles <- rmsle_vs_dih$rmsle
msles <- rmsles * rmsles 
sles <- msles * NUM_PREDICTIONS

err_matrix <- matrix(nrow=16,ncol=16)
for(col in 1:16 ) {
    for(row in 1:16 ) {
        err_matrix[row,col] <- meansqerr(row-1,col-1)
    }
}

# above matrix is symetric, so it's singular
# so replace last row with 'new' information
# so it's solvable
# NOTE: this didn't help -- it's still singular (?!?!!)
row <- 16
for(col in 1:16) { 
    err_matrix[row,col] <- 1 
} 
sles[16] <- NUM_PREDICTIONS


NUM_PREDICTIONS

sles

err_matrix

cat("determinate\n")
print(det(err_matrix))

dih_counts <- solve( err_matrix, sles ) 
dih_counts


