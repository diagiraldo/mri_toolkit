#!/usr/bin/env Rscript

# convert DICOM info (extracted with dcminfo) into a .csv file
# Diana Giraldo, Nov 2023
# Last edit Apr 2026

suppressMessages(library(dplyr))
suppressMessages(library(stringr))
suppressMessages(library(jsonlite))
suppressMessages(library(reshape2))

args = commandArgs(trailingOnly=TRUE)

# Inputs
dcminfo_dir = args[1]
dcmtags_file <- args[2]
# Test example
# dcminfo_dir = "/home/vlab/Downloads/JACHAT82BDC_ENHANCED/JACHAT82BDC_-_ENHANCED/dicom_info"
# dcmtags_file = "/home/vlab/mri_toolkit/data/dicomtags.csv"

# Output dir
output_file = args[3]

# Read DICOM tags names
dcmtags <- read.csv(dcmtags_file)
EXCLUDE_TAGS <- c("0020,0037")

# List of info files
filelist <- list.files(path = dcminfo_dir, pattern = "\\.txt$")
#ndcm <- length(filelist)

tmpdf <- data.frame()
for (filenam in filelist){
  dcminfo_file <- paste(dcminfo_dir, filenam, sep = "/")
  if ( file.size(dcminfo_file) > 0 ){
    linfo <- read.delim(dcminfo_file, header = FALSE) %>%
      mutate(tag = str_extract(V1, "(?<=\\[)(.*?)(?=\\])"),
             value = trimws(str_extract(V1, "(?<=\\] )(.*)"), "right")) %>%
      select(-V1) %>%
      unique(.) %>%
      left_join(., dcmtags, by = "tag") %>%
      filter(!(tag %in% EXCLUDE_TAGS)) %>%
      mutate(Keyword = ifelse(tag == "2001,100B", "SliceOrientation", Keyword),
             Keyword = ifelse(tag == "2005,102A", "MRPatientReferenceID", Keyword)) %>%
      select(Keyword, value)
    # Reshape
    info <- as.data.frame(t(linfo$value))
    names(info) <- make.names(linfo$Keyword)
    # In tmpdf
    tmpdf <- bind_rows(tmpdf, info)
  }
}

# Get series
df <- tmpdf %>% 
  group_by(Series.Description) %>%
  mutate(Start.Time = min(Series.Time),
         End.Time = max(Content.Time),
         n.Instances = max(as.numeric(Instance.Number))) %>%
  ungroup() %>%
  select(-any_of(c("Image.Position.Patient", #"Image.Orientation.Patient", 
                   "Acquisition.Time", "Content.Time", "Series.Time", 
                   "Acquisition.Duration", "Acquisition.Number", "Instance.Number", 
                   "Diffusion.Gradient.Orientation", "DiffusionB.Value"))) %>% 
  unique() %>%
  as.data.frame()

# Write output
write.table(df, 
            file = output_file, 
            sep='\t', row.names = FALSE, quote = TRUE)

