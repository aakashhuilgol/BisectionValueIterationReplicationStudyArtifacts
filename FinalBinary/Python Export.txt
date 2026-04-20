Model types:
------------

network.model_type can have the following values:
"lts" // labelled transition system (LTS)
"ta"  // timed automaton (TA)
"mdp" // Markov decision process (MDP)
"ma"  // Markov automaton (MA)
"pta" // probabilistic timed automaton (PTA)


Properties:
-----------

Atomic propositions:
{ op: "ap", "args": [ index: int ] }  // use the index with network.get_expression_value to evaluate the atomic proposition in a state

State formulas:
!e              -->  { op: "not", args: [ e: PropertyExpression ] }
e1 && e2        -->  { op: "and", args: [ e1: PropertyExpression, e2: PropertyExpression ] }
e1 || e2        -->  { op: "or", args: [ e1: PropertyExpression, e2: PropertyExpression ] }
A e             -->  { op: "forall", args: [ e: PropertyExpression ] }
E e             -->  { op: "exists", args: [ e: PropertyExpression ] }
Pmax(e)         -->  { op: "p_max", args: [ e: PropertyExpression ] }                // numeric
Pmin(e)         -->  { op: "p_min", args: [ e: PropertyExpression ] }                // numeric
Xmax(S(r), e)   -->  { op: "e_max_s", args: [ index: int, e: PropertyExpression ] }  // numeric
Xmin(S(r), e)   -->  { op: "e_min_s", args: [ index: int, e: PropertyExpression ] }  // numeric
Xmax(T(r), e)   -->  { op: "e_max_s", args: [ index: int, e: PropertyExpression ] }  // numeric, for TA and PTA only: rate reward becomes branch reward via digital clocks, use the index in the expressions parameter of network.jump to evaluate the reward expression on a branch
Xmin(T(r), e)   -->  { op: "e_min_s", args: [ index: int, e: PropertyExpression ] }  // numeric, for TA and PTA only: rate reward becomes branch reward via digital clocks, use the index in the expressions parameter of network.jump to evaluate the reward expression on a branch
Xmax(T(r), e)   -->  { op: "e_max_t", args: [ index: int, e: PropertyExpression ] }  // numeric, for MA only, use the index with network.get_expression_value to evaluate the reward expression in a state
Xmin(T(r), e)   -->  { op: "e_min_t", args: [ index: int, e: PropertyExpression ] }  // numeric, for MA only, use the index with network.get_expression_value to evaluate the reward expression in a state

Comparisons:
The numeric state formulas can be turned into Boolean values for states as in e.g. standard definitions of PCTL by adding a comparison ("<=", "<", ">", ">=", "==", or "!="). For example:
Pmax(e1) <= e2  -->  { op: "<=", args: [ { op: "pmax", args: [ e1: PropertyExpression ] }, e2: number ] }  // Boolean, e2 must be a constant expression

Path formulas:
[] e              -->  { op: "always", args: [ e: PropertyExpression ] }
<> e              -->  { op: "eventually", args: [ e: PropertyExpression ] }
true U e          -->  { op: "eventually", args: [ e: PropertyExpression ] }
e1 U e2           -->  { op: "until", args: [ e1: PropertyExpression, e2: PropertyExpression ] }
[][S==1] e        -->  { op: "next", args: [ e: PropertyExpression ] }
<>[S==1] e        -->  { op: "next", args: [ e: PropertyExpression ] }
true U[S==1] e    -->  { op: "next", args: [ e: PropertyExpression ] }
[][S<=e2] e1      -->  { op: "step-bounded-always", args: [ e1: PropertyExpression, e2: int ] }                        // e2 must be a constant integer expression
<>[S<=e2] e1      -->  { op: "step-bounded-eventually", args: [ e1: PropertyExpression, e2: int ] }                    // e2 must be a constant integer expression
true U[S<=e2] e1  -->  { op: "step-bounded-eventually", args: [ e1: PropertyExpression, e2: int ] }                    // e2 must be a constant integer expression
e1 U[S<=e3] e2    -->  { op: "step-bounded-until", args: [ e1: PropertyExpression, e2: PropertyExpression, e3: int ] } // e3 must be a constant integer expression
[][T<=e2] e1      -->  { op: "time-bounded-always", args: [ e1: PropertyExpression, e2: int ] }                        // e2 must be a constant expression, for MA only
<>[T<=e2] e1      -->  { op: "time-bounded-eventually", args: [ e1: PropertyExpression, e2: int ] }                    // e2 must be a constant expression, for MA only
true U[T<=e2] e1  -->  { op: "time-bounded-eventually", args: [ e1: PropertyExpression, e2: int ] }                    // e2 must be a constant expression, for MA only
e1 U[T<=e3] e2    -->  { op: "time-bounded-until", args: [ e1: PropertyExpression, e2: PropertyExpression, e3: int ] } // e3 must be a constant expression, for MA only

To obtain the value of a branch/transition reward with index r (e.g. from the "emax" operator), include that index in the "expressions" array of the jump/jump_np methods. If r was passed in at index i, then when the method returns, the value at index i will be the branch/transition reward value on that branch/transition.
