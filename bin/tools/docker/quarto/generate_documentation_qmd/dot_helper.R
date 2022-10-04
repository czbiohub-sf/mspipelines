# assumes 'tidyverse' and 'rlang' are loaded

read_dot <- function(path) {
  lines <- readr::read_lines(path)

  # split dot lines between nodes and edges
  node_regex <- "^([^ ]*)(| \\[([^\\]*)\\]);$"
  node_lines <- lines[grepl(node_regex, lines)]
  edge_regex <- "^([^ ]*) -> ([^ ]*)(| \\[([^\\]*)\\]);$"
  edge_lines <- lines[grepl(edge_regex, lines)]

  # read nodes
  node_df <-
    map_df(node_lines, function(line) {
      node_id <- gsub(node_regex, "\\1", line)
      props <- gsub(node_regex, "\\3", line) %>% strsplit(",") %>% .[[1]]
      props_parsed <- sapply(strsplit(props, "="), function(x) setNames(gsub("^\"|\"$", "", x[[2]]), x[[1]]))
      as_tibble(c(list(node_id = node_id), as.list(props_parsed)))
    }) %>%
    unique %>%
    mutate(
      orig_label = label,
      # determine new label
      label = case_when(
        label != "" ~ gsub(".*:([^:]*)_process$", "\\1", label),
        is.na(xlabel) ~ "Output",
        xlabel == "Channel.fromList" ~ "Input",
        TRUE ~ xlabel
      )
    )

  # read edges
  edge_df <- map_df(edge_lines, function(line) {
    from <- gsub(edge_regex, "\\1", line)
    to <- gsub(edge_regex, "\\2", line)
    props <- gsub(edge_regex, "\\4", line) %>% strsplit(",") %>% .[[1]]
    props_parsed <- sapply(strsplit(props, "="), function(x) setNames(gsub("^\"|\"$", "", x[[2]]), x[[1]]))
    as_tibble(c(list(from = from, to = to), as.list(props_parsed)))
  })
  list(nodes = node_df, edges = edge_df)
}

remove_nodes_replace_edges <- function(graph, to_remove) {
  edges <- graph$edges

  for (n in to_remove) {
    edges_to <- edges %>% filter(to == n) %>% select(from, rem = to)
    edges_from <- edges %>% filter(from == n) %>% select(rem = from, to)
    edges_remain <- edges %>% filter(from != n, to != n)
    edges <- bind_rows(
      edges_remain,
      full_join(edges_to, edges_from, by = "rem") %>% select(-rem)
    )
  }
  nodes <- graph$nodes %>% filter(!node_id %in% to_remove)

  list(nodes = nodes, edges = edges)
}

graph_to_dot <- function(graph) {
  node_lines2 <-
    graph$nodes %>%
    mutate_at(vars(label), function(x) ifelse(is.na(x), NA_character_, paste0("\"", x, "\""))) %>%
    select(-xlabel, -orig_label) %>%
    transpose() %>%
    map_chr(function(li) {
      lif <- unlist(li[names(li) != "node_id"])
      lif2 <- lif[!is.na(lif) & lif != ""]
      paste0(li$node_id, " [", paste(paste0(names(lif2), "=", unname(lif2)), collapse = ","), "];")
    })

  edge_lines2 <- 
    paste0(graph$edges$from, " -> ", graph$edges$to, ";")

  c("digraph \"graph\" {", node_lines2, edge_lines2, "}")
}

graph_to_mermaid <- function(graph) {
  node_lines2 <-
    graph$nodes %>%
    transpose() %>%
    map_chr(function(li) {
      lif <- li[names(li) != "node_id"]
      lif2 <- lif[!is.na(lif) & lif != ""]
      label <- lif2[["label"]] %||% lif2[["xlabel"]] %||% "Output"
      # assume if no label is present it's always an output
      if (is.null(label)) {
        ""
      } else {
        paste0("    ", li$node_id, "(", label, ")")
      }
    })

  edge_lines2 <-
    paste0("    ", graph$edges$from, "-->", graph$edges$to)

  c("flowchart LR", node_lines2, edge_lines2)
}

process_dot <- function(input, format) {
  graph0 <- read_dot(input)

  ############### CLEANUP ROUND 1 ###############
  to_remove0 <- graph0$nodes %>% filter(label %in% c("map", "view")) %>% .$node_id

  graph1 <- remove_nodes_replace_edges(graph0, to_remove0)

  ############### CLEANUP ROUND 2 ###############

  comb <- graph1$edges %>%
    left_join(graph1$nodes %>% select(from = node_id, from_lab = label), by = "from") %>% 
    left_join(graph1$nodes %>% select(to = node_id, to_lab = label), by = "to")

  to_remove1 <-
    comb %>%
    filter(from_lab == "toList", to_lab == "Output") %>%
    .$from

  graph2 <- remove_nodes_replace_edges(graph1, to_remove1)

  ############### CONVERT BACK TO GRAPH FILE ###############
  graph_lines <-
    if (format == "dot") {
      graph_to_dot(graph2)
    } else {
      graph_to_mermaid(graph2)
    }

  graph_lines
}