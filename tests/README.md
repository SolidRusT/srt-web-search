# Agent Tests

This document outlines the test cases for the various agents implemented in the project. Each section provides detailed test steps and expected outcomes for the Chat Agent, WebSearch Agent, and Wiki Agent.

## Chat Agent tests

### Test Case 1: Basic Interaction

**Description**: Test basic interaction with the Chat Agent.
**Steps**:

1. Launch the application with the Chat Agent mode.

   ```bash
   python main.py --mode chat --interface gradio
   ```

2. Enter a simple query: "Hello, how are you?"
3. Observe the response.

**Expected Result**: The Chat Agent should respond with a friendly greeting and an appropriate response to the query.

### Test Case 2: Complex Query

**Description**: Test the Chat Agent's ability to handle a more complex query.
**Steps**:

1. Launch the application with the Chat Agent mode.

   ```bash
   python main.py --mode chat --interface gradio
   ```

2. Enter a complex query: "Can you explain the theory of relativity?"
3. Observe the response.

**Expected Result**: The Chat Agent should provide a detailed explanation of the theory of relativity.

## WebSearch Agent tests

### Test Case 1: Simple Web Search

**Description**: Test the WebSearch Agent's ability to perform a simple web search.
**Steps**:

1. Launch the application with the WebSearch Agent mode.

   ```bash
   python main.py --mode web_search --interface gradio
   ```

2. Enter a query: "What is the capital of France?"
3. Observe the response.

**Expected Result**: The WebSearch Agent should provide a response with information about the capital of France.

### Test Case 2: Research Document Generation

**Description**: Test the WebSearch Agent's ability to generate a detailed research document based on a user query.
**Steps**:

1. Launch the application with the WebSearch Agent mode.

   ```bash
   python main.py --mode web_search --interface gradio
   ```

2. Enter a query: "Write a detailed report on the impact of climate change."
3. Observe the response.

**Expected Result**: The WebSearch Agent should generate a detailed research document on the impact of climate change, citing sources appropriately.

## Wiki Agent tests

### Test Case 1: List of Nobel laureates

**Description**: Test the Wiki Agent's ability to retrieve and summarize information from a specific Wikipedia page.
**Page Title**: `List_of_Nobel_laureates`
**Steps**:

1. Launch the application with the Wiki Agent mode.

   ```bash
   python main.py --mode wikipedia --interface gradio
   ```

2. Enter the page title: `List_of_Nobel_laureates`.
3. Enter the query: "List the Nobel laureates from 1999."
4. Observe the response.
5. Enter the query: "What were the prizes given to the winners?"
6. Observe the response.

**Expected Results**:

- The Wiki Agent should list the Nobel laureates from 1999.
- The Wiki Agent should provide information on the prizes given to the winners in 1999.

### Test Case 2: Synthetic diamond

**Description**: Test the Wiki Agent's ability to retrieve specific technical information from a Wikipedia page.
**Page Title**: `Synthetic_diamond`
**Steps**:

1. Launch the application with the Wiki Agent mode.

   ```bash
   python main.py --mode wikipedia --interface gradio
   ```

2. Enter the page title: `Synthetic_diamond`.
3. Enter the query: "What is a BARS apparatus?"
4. Observe the response.

**Expected Result**: The Wiki Agent should provide a detailed explanation of a BARS apparatus.

### Test Case 3: Ecuadorian security crisis

**Description**: Test the Wiki Agent's ability to retrieve and summarize complex information from a Wikipedia page.
**Page Title**: `Ecuadorian_security_crisis`
**Steps**:

1. Launch the application with the Wiki Agent mode.

   ```bash
   python main.py --mode wikipedia --interface gradio
   ```

2. Enter the page title: `Ecuadorian_security_crisis`.
3. Enter the query: "Tell me about what is going on the Ecuadorian security crisis?"
4. Observe the response.
5. Enter the query: "Who are the criminal groups in Ecuador?"
6. Observe the response.
7. Enter the query: "Who are Choneros?"
8. Observe the response.

**Expected Results**:

- The Wiki Agent should provide a detailed overview of the current Ecuadorian security crisis.
- The Wiki Agent should list and describe the criminal groups in Ecuador.
- The Wiki Agent should provide information about the Choneros group.
