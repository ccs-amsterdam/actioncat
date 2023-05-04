for (p in c("attachment", "pak", "remotes")) {
  if (!requireNamespace(p, quietly = TRUE)) install.packages(p)
}

deps <- attachment::att_from_rscripts(path = ".")
deps <- setdiff(deps, c(installed.packages()[, 1], "amcat4r"))
reqs <- remotes::system_requirements("ubuntu", "20.04", package = deps)
system2(reqs)
pak::pkg_install(deps)
remotes::install_github("ccs-amsterdam/amcat4r")
