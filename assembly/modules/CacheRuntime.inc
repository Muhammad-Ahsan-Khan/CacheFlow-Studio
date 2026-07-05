; ============================================================================
; CacheFlow Studio - Runtime support
; ============================================================================

ResetSimulationState PROC
    pushad

    mov hitCount, 0
    mov missCount, 0
    mov completedRequests, 0
    mov fifoCursor, 0
    mov lruClock, 0

    mov esi, OFFSET cacheLines
    mov edi, OFFSET lruTimestamps
    mov ecx, CACHE_LINE_COUNT

ResetLineLoop:
    mov DWORD PTR [esi], EMPTY_CACHE_LINE
    mov DWORD PTR [edi], 0
    add esi, TYPE cacheLines
    add edi, TYPE lruTimestamps
    loop ResetLineLoop

    popad
    ret
ResetSimulationState ENDP

GenerateMemoryAccess PROC
    push eax
    push ebx

    mov eax, MEMORY_WORD_COUNT
    call RandomRange
    mov currentIndex, eax

    mov ebx, eax
    shl ebx, 2
    mov eax, memoryWords[ebx]
    mov currentValue, eax

    pop ebx
    pop eax
    ret
GenerateMemoryAccess ENDP

PauseBetweenSteps PROC
    push eax
    mov eax, 650
    call Delay
    pop eax
    ret
PauseBetweenSteps ENDP

PauseDuringSearch PROC
    push eax
    mov eax, 350
    call Delay
    pop eax
    ret
PauseDuringSearch ENDP
