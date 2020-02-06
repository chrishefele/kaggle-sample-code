
library(rhdf5)

# Adapted from http://pandas.pydata.org/pandas-docs/stable/io.html#io-external-compatibility 

read_hdf <- function(h5path, dataframe_name=NULL) {

    h5File <- H5Fopen(h5path, flags="H5F_ACC_RDONLY")
    listing <- h5ls(h5File)
      
    if (is.null(dataframe_name)) {
        dataframe_name <- listing$name[1]
    }

    group_name <- paste0("/", dataframe_name)

    # Filter to just the requested dataframe:
    listing <- listing[listing$group == group_name,]

    # Find all data nodes, values are stored in *_values and corresponding column
    # titles in *_items
    data_nodes <- grep("_values$", listing$name)
    name_nodes <- grep("_items$", listing$name)
    data_paths = paste(listing$group[data_nodes], listing$name[data_nodes], sep = "/")
    name_paths = paste(listing$group[name_nodes], listing$name[name_nodes], sep = "/")
    columns = list()

    for (idx in seq(data_paths)) {
        # NOTE: matrices returned by h5read have to be transposed to to obtain
        # required Fortran order!
        data <- data.frame(t(h5read(h5File, data_paths[idx])))
        names <- t(h5read(h5File, name_paths[idx]))
        entry <- data.frame(data)
        colnames(entry) <- names
        columns <- append(columns, entry)
    }

    data <- data.frame(columns)

    # If "axis0" is specified, we can return the dataframe columns in the original order:
    if ("axis0" %in% listing$name) {
        orig_col_order <- h5read(h5File, paste0(group_name, "/axis0"))
        data <- data[orig_col_order]
    }

    H5Fclose(h5File)
    return(data)
}

# train <- read_hdf("../../download/train.h5")
# print(head(train))
