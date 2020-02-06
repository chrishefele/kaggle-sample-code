DATA_FILE = '../data/test_altgspd_vs_dist.csv'
# arrival_distance,altitude,groundspeed

PLOT_FILE = '../plots/test_altgspd_vs_dist.pdf'
pdf(file=PLOT_FILE)

df <- read.csv(DATA_FILE)

PCH <- '.'
YLIM_ALT  <- c(0, 45000)
YLIM_GSPD <- c(0, 600)
XLIM_DIST <- c(0,2000)


scatter.smooth(df$arrival_distance, df$altitude,    type='n', xlim=XLIM_DIST, ylim=YLIM_ALT, 
        pch=PCH, main="Altitude vs ArrivalDistance")
scatter.smooth(df$arrival_distance, df$groundspeed, type='n', xlim=XLIM_DIST, ylim=YLIM_GSPD,
        pch=PCH, main="Groundspeed vs ArrivalDistance")

scatter.smooth(df$arrival_distance, df$altitude,    type='n', pch=PCH, main="Altitude vs ArrivalDistance")
scatter.smooth(df$arrival_distance, df$groundspeed, type='n', pch=PCH, main="Groundspeed vs ArrivalDistance")

cat('wrote plots to: ', PLOT_FILE, '\n')


