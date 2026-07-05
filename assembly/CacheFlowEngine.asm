; ============================================================================
; CacheFlow Studio - MASM / Irvine32 Console Engine
; Refactored from the original COAL cache hit/miss simulator.
; The cache model and FIFO/LRU behavior are preserved while the program is
; reorganized into focused modules.
; ============================================================================

INCLUDE Irvine32.inc
INCLUDE modules\CacheFlowModel.inc

.code
main PROC
    call Randomize
    call ResetSimulationState
    call RenderWelcomeScreen
    call CapturePolicyChoice
    call RenderSimulationHeader
    call ExecuteRequestCycle
    call RenderFinalReport
    exit
main ENDP

; ----------------------------------------------------------------------------
; Runs the configured number of random memory requests.
; ----------------------------------------------------------------------------
ExecuteRequestCycle PROC
    pushad
    mov ecx, configuredRequests

RequestCycle:
    call PauseBetweenSteps
    call RenderStepDivider
    call GenerateMemoryAccess
    call RenderCurrentRequest
    call RenderSearchMessage
    call PauseDuringSearch

    cmp activePolicy, POLICY_LRU
    je UseLruPolicy
    call ApplyFifoPolicy
    jmp RequestHandled

UseLruPolicy:
    call ApplyLruPolicy

RequestHandled:
    call RenderCacheSnapshot
    inc completedRequests
    dec ecx
    jnz RequestCycle

    popad
    ret
ExecuteRequestCycle ENDP

INCLUDE modules\CacheRuntime.inc
INCLUDE modules\CachePolicies.inc
INCLUDE modules\ConsoleViews.inc

END main
