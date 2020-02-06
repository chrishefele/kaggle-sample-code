r <- read.csv("results.csv")
# rmse_public, rmse_private, rmse_all, regularization
pdf("results.plot.pdf")
plot(log10(r$regularization), r$rmse_public,  type="b", main="Public & Private RMSEs vs Regularization; 3 file blend")
plot(log10(r$regularization), r$rmse_private, type="b")
plot(log10(r$regularization), r$rmse_all,     type="b")

miny <- min(r$rmse_public, r$rmse_private)
maxy <- max(r$rmse_public, r$rmse_private)

plot( log10(r$regularization), r$rmse_public,  type="b", ylim=c(miny, maxy), main="Public & Private RMSEs vs Regularization; 3 file blend")
lines(log10(r$regularization), r$rmse_private, type="b")

plot( log10(r$regularization), r$rmse_public - r$rmse_private,  type="b", main="Public & Private RMSE gap vs Regularization; 3 file blend")
