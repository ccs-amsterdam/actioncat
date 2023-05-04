library(amcat4r)
library(tidytext)
library(dplyr)
library(tidyr)

# set variables
index <- Sys.getenv("index")
text_field <- Sys.getenv("text_field")
dfm_field <- Sys.getenv("dfm_field")
amcat4_host <- Sys.getenv("amcat4_host")
queries <- NULL
if (!Sys.getenv("queries") %in% c("", "NULL")) {
  queries <- Sys.getenv("queries")
}

# retrieve token
amcat_login(amcat4_host)

# download text
text_data <- query_documents(index = index, queries = NULL, fields = c(".id", text_field))

# convert text to tidy-dfm
text_data_dfm <- text_data %>% 
  unnest_tokens("feature", "text") %>% 
  count(.id, feature)

# add dfm to text_data and remove text
text_data_new <- text_data %>% 
  mutate(dfm = lapply(.id, function(id) {
    text_data_dfm %>% 
      filter(.id == id) %>% 
      select(-.id)
  })) %>% 
  select(-text)

# upload dfm
set_fields(index = index, list(dfm = "object"))
update_documents(index = index, documents = text_data_new)

##  guests can now query the dfm with 
# text_data_new <- query_documents(index = index, queries = NULL, fields = c(".id", "dfm")) %>% 
#   unnest(dfm) %>% 
#   unnest_wider(dfm)
                             