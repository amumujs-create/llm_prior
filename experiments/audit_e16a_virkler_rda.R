# Read-only R audit for the pinned E16-A Virkler source artifact.
# Usage: Rscript audit_e16a_virkler_rda.R /path/to/Virkler.rda

args <- commandArgs(trailingOnly = TRUE)
if (length(args) != 1L) stop("Provide exactly one path to Virkler.rda")

source_path <- args[[1L]]
e <- new.env(parent = emptyenv())
load(source_path, envir = e)
if (!exists("Virkler", envir = e, inherits = FALSE)) stop("Virkler object absent")

V <- get("Virkler", envir = e, inherits = FALSE)
stopifnot(is.data.frame(V), identical(dim(V), c(164L, 69L)))
stopifnot(identical(names(V)[[1L]], "CrackLength"))
stopifnot(identical(names(V)[2:69], paste0("CycleCount", 1:68)))

stopifnot(sum(is.na(V)) == 0L)
stopifnot(all(is.finite(as.matrix(V))))

a <- V[[1L]]
N <- as.matrix(V[, -1L])
stopifnot(anyDuplicated(a) == 0L, all(diff(a) > 0))
stopifnot(all(apply(N, 2L, function(z) all(diff(z) >= 0))))

print(list(
  object_names = ls(e),
  dimension = dim(V),
  crack_length_endpoints_mm = c(a[[1L]], a[[length(a)]]),
  min_within_trajectory_cycle_increment = min(diff(N))
))
