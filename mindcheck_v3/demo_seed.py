"""Teacher-approved ReLU demonstration check. Stable across app restarts."""
DEMO_CODE = "RELU-DEMO"
DEMO_SCOPE = {
    "topic": "ReLU Activation Function in Neural Networks",
    "objectives": (
        "Explain how the ReLU activation function transforms input values.\n"
        "Explain why ReLU introduces non-linearity into a neural network.\n"
        "Apply the ReLU function correctly to numerical inputs.\n"
        "Use knowledge of ReLU to reason about its behavior in a new or unfamiliar neural-network situation."
    ),
    "required_concepts": "ReLU\nmax(0, x)\nnegative inputs become 0\npositive inputs remain unchanged\nactivation function\nnon-linearity",
    "out_of_scope": (
        "Detailed backpropagation mathematics\nDerivative calculations\n"
        "Historical development of activation functions\n"
        "Detailed comparison with sigmoid, tanh, GELU, or other activation functions\n"
        "Advanced optimization algorithms"
    ),
    "strictness": "Balanced",
}
DEMO_SOURCE = (
    "ReLU (Rectified Linear Unit) is an activation function commonly used in neural networks. "
    "It is defined as f(x) = max(0, x). Negative inputs output 0; zero outputs 0; "
    "positive inputs remain unchanged. ReLU introduces non-linearity, helping neural "
    "networks represent more complex relationships than stacked linear transformations."
)
DEMO_QUESTIONS = {
    "explain": {
        "objective": "Explain how ReLU transforms inputs and why non-linearity is useful.",
        "question": "In your own words, explain how ReLU transforms an input value and why this function is useful in a neural network."
    },
    "apply": {
        "objective": "Apply ReLU correctly to numerical inputs and explain the calculation.",
        "question": "A neuron receives the values -4, -1, 0, 3, and 7 before activation. Apply ReLU to these values and explain how you obtained your answer."
    },
    "transfer": {
        "objective": "Reason about the effect of adding ReLU to a network with only linear transformations.",
        "question": "Imagine a neural network layer in which every neuron uses only a linear transformation and no activation function. What could change if ReLU is introduced after the linear transformation? Explain your reasoning."
    }
}
