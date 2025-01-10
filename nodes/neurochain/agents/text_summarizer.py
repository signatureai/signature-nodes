from typing import Literal

from neurochain.agents.text_summarizer import TextSummarizer as TextSummarizerNeurochain
from neurochain.llms.entities import BaseLLM

from ...categories import AGENT_CAT

DEFAULT_TEXT = """# Deep Learning

## Introduction
Deep learning is a subset of machine learning in artificial intelligence (AI) that has networks capable of learning from data that is unstructured or unlabeled. Also known as deep neural learning or deep neural network.

## How It Works
Deep learning models are based on artificial [[neural networks]] (ANNs) with multiple layers, hence the term "deep." These models are designed to mimic the way the human brain processes information, allowing them to identify patterns and make decisions with minimal human intervention.

## Key Components
1. **[[Neural Networks]]**: The foundation of deep learning, consisting of layers of nodes (neurons) that process input data and pass it through the network.
2. **Layers**:
   - **Input Layer**: The initial layer that receives the raw data.
   - **Hidden Layers**: Intermediate layers that perform computations and extract features from the data.
   - **Output Layer**: The final layer that produces the prediction or classification result.
3. **[[Activation Functions]]**: Functions that determine whether a neuron should be activated or not, introducing non-linearity into the model.
4. **Loss Function**: A function that measures the difference between the predicted output and the actual output, guiding the training process.
5. **Optimization Algorithms**: Methods used to adjust the weights of the network to minimize the loss function, such as [[gradient descent]].

## Applications
Deep learning has a wide range of applications, including:
- **Image and Speech Recognition**: Identifying objects in images or transcribing spoken words into text.
- **Natural Language Processing (NLP)**: Understanding and generating human language, such as in chatbots and translation services.
- **Autonomous Vehicles**: Enabling self-driving cars to perceive and navigate their environment.
- **Healthcare**: Assisting in diagnosis and treatment planning by analyzing medical images and patient data.

## Conclusion
Deep learning is a powerful and rapidly evolving field that is transforming various industries by enabling machines to learn from vast amounts of data and perform complex tasks with high accuracy. As research and technology continue to advance, the potential applications and impact of deep learning are expected to grow even further."""


class TextSummarizer:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "text": ("STRING", {"multiline": True, "default": DEFAULT_TEXT}),
                "llm": ("LLM", {}),
                "strategy": (["independent", "iterative"], {"default": "independent"}),
            },
            "optional": {
                "chunk_size": ("INT", {"default": 1000}),
                "chunk_overlap": ("INT", {"default": 30}),
            },
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("response",)
    FUNCTION = "process"
    CATEGORY = AGENT_CAT
    OUTPUT_NODE = True

    def process(
        self,
        text: str,
        llm: BaseLLM,
        strategy: Literal["independent", "iterative"],
        chunk_size: int,
        chunk_overlap: int,
    ):
        text_summarizer = TextSummarizerNeurochain(llm=llm, chunk_size=chunk_size, chunk_overlap=chunk_overlap)
        response = text_summarizer.summarize(text, strategy=strategy)
        return (response,)
