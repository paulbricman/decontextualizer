---
title: Decontextualizer
emoji: 📤
colorFrom: green
colorTo: gray
sdk: streamlit
app_file: main.py
pinned: false
---


![](https://paulbricman.com/assets/img/decontextualizer_featured.png)
# Decontextualizer

As a second step in improving our content consumption workflows, I investigated a new approach to extracting fragments from a content item before saving them for subsequent surfacing. While the [lexiscore](https://paulbricman.com/thoughtware/lexiscore) deals with content items on a holistic level -- evaluating entire books, articles, and papers -- I speculated then that going granular is a natural next step in building tools which help us locate *specific* valuable ideas in long-form content. The decontextualizer is a stepping stone in that direction, consisting of a pipeline for making text excerpts compact and semantically self-contained. Concretely, the decontextualizer is a web app able to take in an annotated PDF and automatically tweak the highlighted excerpts so that they make more sense on their own, even out of context.

[Read more...](https://paulbricman.com/thoughtware/decontextualizer)

# Installation

The decontextualizer can either be deployed from source or using Docker.

### Docker

To deploy the decontextualizer labeler using Docker, first make sure to have Docker installed, then simply run the following.

```
docker run -p 8501:8501 paulbricman/decontextualizer 
```

The tool should be available at `localhost:8501`.

### From Source

To set up the decontextualizer, clone the repository and run the following:

```
python3 -m pip install -r requirements.txt
streamlit run main.py
```

The tool should be available at `localhost:8501`.

# Screenshots

![](https://paulbricman.com/assets/img/decontextualizer_mockup.png)
