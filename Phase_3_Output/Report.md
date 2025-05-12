# StillOnPentium
Authors: Chitraksh,Sandeep
ID: CS23B054, CS23B050

---
## Implementation Report

### How did you merge the four compute unit? How do the compute units share the data and instruction memory?

*Ans:* In Phase 1 of the simulator, each of the four compute units had bounded access to a shared memory module. Although the memory was technically shared, the restricted access made it functionally similar to having private memory for each compute unit. Additionally, each compute unit maintained its own instruction array, allowing them to fetch and execute instructions independently.

In Phase 2, we merged the instruction and memory systems by removing the bounded access. We introduced a single shared memory module for all compute units, and stored instructions directly in this shared memory. A centralized fetch unit was also introduced to handle instruction fetching for all compute units. If all compute units were operating at the same program counter (PC) value, the fetch unit would retrieve the instruction once and broadcast it to all units. However, if compute units had different PC values, the fetch unit would fetch instructions individually based on each unit's PC. This shared memory system also supports data access in a similar centralized manner.

### In a parallel computing setup where all compute units share the same instruction and data memory, and each unit updates a shared variable sum, how can we ensure that the updates to sum are correct and free from interference? Would the following approach work?

*Ans:* Yes, this approach would work and is a valid method to avoid race conditions in a shared memory system. By assigning each compute unit its own index in the sum[] array, we ensure that each unit writes to a separate memory location during the summation loop. This avoids simultaneous writes to the same variable, eliminating interference.

Later, a single compute unit (e.g., CID == 1) is responsible for combining the partial results from all compute units. Since this happens after the initial summation and is performed by only one unit, there are no concurrency issues during the final aggregation either.

## Cache Implementation 

We have implemented a multi-level cache system consisting of two levels of cache (L1 and L2) followed by main memory. The latencies, associativities, and sizes of these memory levels are user-configurable, providing flexibility in simulation.

At the first level (L1), we include L1D (Data) and L1I (Instruction) caches, both having the same latency. These L1 caches are shared among all compute units. Following L1, we have the L2 cache, which is also shared across all cores and is capable of holding cache lines from both L1D and L1I. Beyond this lies the main memory, which stores program instructions, actual data, and scratchpad memory.

During the initialization phase, we compute the index bits, offset bits, and tag bits for the cache. This enables efficient cache line identification and accurate data retrieval.

We support two replacement policies for cache management:
- LRU (Least Recently Used)
- NRU (Not Recently Used)

Both policies are implemented using standard algorithms and are responsible for selecting which cache line to evict during a miss. The user can pre-select the desired replacement policy before execution.

Each cache level is associated with a specific latency, and this latency is used to stall the pipeline during memory access. A central function called memory_system() orchestrates the cache lookup process, manages cache misses, retrieves data from main memory when needed, and updates the cache accordingly.

This architecture ensures an efficient and customizable cache simulation mechanism for handling memory operations.

## SYNC Implementation

To implement hardware-level synchronization, we use a queue to track which cores are active and two boolean arrays: sync_reached[] and instructions_fetch_possible[]. The sync_reached[] array marks whether each core has encountered a sync instruction, while instructions_fetch_possible[] controls whether a core is allowed to fetch new instructions or is stalled.

Initially, all values in sync_reached[] are set to false. When a core reaches a sync, its corresponding entry in sync_reached[] is set to true. We then check if all cores have reached the sync point simultaneously (e.g., same PC or no branching divergence). If so, we resume execution for all cores by resetting sync_reached[] and ensuring all entries in instructions_fetch_possible[] remain true.

However, if a core reaches sync early (due to branching or execution speed differences), we stall it by setting instructions_fetch_possible[cid] = false. It will remain stalled until all other cores also reach the sync point. Once every core has reached the barrier, we reset the stalled core and allow it to resume execution. This mechanism ensures proper synchronization across compute units.

## ScratchPad Memory

The *scratchpad memory* functions similarly to the main memory in terms of *read and write operations, but with **significantly lower latency. It resides at the **same level as the L1 Data Cache (L1D)* in the memory hierarchy, offering faster access compared to main memory. To interact with the scratchpad, we introduce two special instructions: lw_spm (load word from scratchpad) and sw_spm (store word to scratchpad). These instructions allow compute units to explicitly load data from and store data to the scratchpad, making it suitable for time-critical or frequently accessed data.