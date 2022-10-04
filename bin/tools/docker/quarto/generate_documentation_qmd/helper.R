viash_ns_list <- function(src, parse_argument_groups = FALSE, platform = NULL) {
  args <- c("ns", "list", "--src", src)

  if (parse_argument_groups) {
    args <- c(args, "--parse_argument_groups")
  }
  if (!is.null(platform)) {
    args <- c(args, "--platform", platform)

  }
  out <- processx::run(
    "viash",
    args = args,
    error_on_status = FALSE
  )

  yaml::yaml.load(out$stdout)
}

jinja <- function(template, data = NULL, output = NULL) {
  args <- c(template)
  
  if (!is.null(data)) {
    if (is.character(data) && fs::is_file(data)) {
      # if data is a file, simply pass it to jinja
      args <- c(args, "--data", data)
    } else {
      # else, write R object as a yaml and pass that to jinja
      temp_file <- tempfile("jinja_data", fileext = ".yaml")
      on.exit(file.remove(temp_file))
      yaml::write_yaml(data, temp_file)
      args <- c(args, "--data", temp_file)
    }
  }
  if (!is.null(output)) {
    args <- c(args, "--output", output)
  }

  processx::run("jinja", args)
}