# Using workflow step labels

Workflow steps may be manually ordered and redirected by use of `GoToStep` and step labels.

Workflow steps can be labelled by passing a label string as an argument to the `step` decorator.

Workflow ordering can be preempted and redirected by raising the `GoToStep` exception, passing either the workflow step label or its numeric index.

Workflows may also be advanced directly to completion by rasing the `GoToEnd` exceptions.


## Defining workflow labels

The following workflow contains five steps in total, which are executed in a specific order as directed by the labels.

```py title="my_labelled_workflow.py"
from ergate import GoToEnd, GoToStep, Workflow

workflow = Workflow(unique_name="my_second_workflow")

@workflow.step
def step_1() -> None:
    print("Hello, I am step 1")

@workflow.label("step_2")
@workflow.step
def step_2() -> None:
    print("Hello, I am step 2")
    raise GoToStep(label="step_3")

@workflow.label("step_5")
@workflow.step
def step_5() -> None:
    print("Hello, I am step 5")
    raise GoToEnd

@workflow.label("step_3")
@workflow.step
def step_3() -> None:
    print("Hello, I am step 3")

@workflow.step
def step_4() -> None:
    print("Hello, I am step 4")
    raise GoToStep(label="step_5")
```

`step_1` and `step_2` execute in normal sequence order.  However, `step_2` raises the `GoToStep` exception for `step_3`,
which redirects the execution order.  `step_3` executes and then proceeds to `step_4` by normal sequence order, but 
`step_4` also raises `GoToStep` for `step_5`, redirecting the order back to that function.  Finally, `step_5` executes, 
and then raises `GoToEnd` to complete the workflow and prevent `step_3` and `step_4` from being run again from the 
normal function sequencing.

The resulting order is:

1. `step_1`
2. `step_2`
3. `step_3`
4. `step_4`
5. `step_5`

Without the `GoToStep` and `GoToEnd` exceptions being utilised, this workflow would execute in the source ordering:

1. `step_1`
2. `step_2`
3. `step_5`
4. `step_3`
5. `step_4`

This trivial example may seem pointless, as one could readily move `step_5` to the end of the file and negate the need 
for these exceptions and labels.  However, these features allow for branching of workflows according to arbitrary 
conditions.

Consider the following bifurcated workflow.

```py title="my_labelled_workflow.py"
from ergate import GoToEnd, GoToStep, Workflow

workflow = Workflow(unique_name="my_second_workflow")

@workflow.step
def step_1(input_value) -> None:
    print("Hello, I am step 1")
    
    match input_value:
        case "a":
            raise GoToStep("step_a2")
        case "b":
            raise GoToStep("step_a2")
        case _:
            raise GoToStep("step_default2")

@workflow.label("step_default")
@workflow.step
def step_default2() -> None:
    print("Hello, I am step default.2")
    raise GoToStep(label="step_4")

@workflow.label("step_a2")
@workflow.step
def step_a2() -> None:
    print("Hello, I am step a.2")

def step_a3() -> None:
    print("Hello, I am step a.3")
    raise GoToStep(label="step_4")

@workflow.label("step_b2")
@workflow.step
def step_b2() -> None:
    print("Hello, I am step b.2")

def step_b3() -> None:
    print("Hello, I am step b.3")
    raise GoToStep(label="step_4")

@workflow.label("step_4")
@workflow.step
def step_4() -> None:
    print("Hello, I am step 4")
```

In this case, there are three possible paths for the workflow to take, based on the value of `input_value`:

If `input_value` is `a`, the workflow path is:

1. `step_1`
2. `step_a2`
3. `step_a3`
4. `step_4`

If `input_value` is `b`, the workflow path is:

1. `step_1`
2. `step_b2`
3. `step_b3`
4. `step_4`


If `input_value` is anything else, the workflow path is:

1. `step_1`
2. `step_default2`
4. `step_4`

Note that the length of the workflows can vary.

## Errata
* Because of how the `percent_completed` and `total_steps` values are calculated, utilising step labels and these 
exceptions can cause the percentage and step calculations to be inaccurate.  However, since the workflow will always 
reach the end, either by normal sequence order or by use of `GoToEnd`, the final step will always complete as 100%.

* `@workflow.label` must precede `@workflow.step` in the source code (i.e. `label` wraps `step`), since `label` depends 
upon values generated within `step`.   A `ValueError` will be raised if they are put out of order.