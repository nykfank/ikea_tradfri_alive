library(data.table)
library(rjson)
cfg <- fromJSON(file="/opt/ikea_tradfri_config.txt")

# Load and prepare data
tradfri_log <- fread(cfg[["logfile"]]) # Load logfile created by ikea_tradfi_alive.py
colnames(tradfri_log) <- c("timestamp", "bulb", "alive", "power", "brightness", "warmth") # Add column headers
tradfri_log$ptime <- as.POSIXct(tradfri_log$timestamp, origin="1970-01-01") # Convert unix timestamp
tradfri_log$time <- strftime(tradfri_log$ptime, "%H:%M") # Create hour:minute variable

# Subset 24 hours
tradfri_day <- tradfri_log[timestamp > max(timestamp) - 60*60*24, ] # Extract last 24 hours of log
#tradfri_day <- tradfri_log[as.Date(ptime) == as.Date("2018-09-21"), ] # Alternatively extract specified day

# Verify data
minuteSeconds <- seq(from=0, to=60*60*24, by=60)
minutes <- strftime(as.POSIXct(minuteSeconds, origin="1970-01-01"), "%H:%M", tz="UTC")
missing_minutes <- sum(!minutes %in% tradfri_day$time)
sprintf("%d of %d (%2.1f%%) missing", missing_minutes, length(minutes), 100*missing_minutes/length(minutes))

# Prepare data for tradfi_bulbGhost.py
tradfri_day[alive == 0 & power == 1, "power"] <- 0 # Not alive -> no power
tradfri_day <- tradfri_day[,c("bulb", "time", "power", "brightness", "warmth")] # Select required columns
print(table(tradfri_day$bulb, tradfri_day$power)) # Tabulate number of ON minutes per bulb and day
fwrite(tradfri_day, file=cfg[["dayfile"]], sep="\t", col.names = FALSE) # Save as TSV text
