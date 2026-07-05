; ============================================================================
; CacheFlow Studio - FIFO and LRU replacement policies
; ============================================================================

ApplyFifoPolicy PROC
    pushad

    mov esi, OFFSET cacheLines
    mov ecx, CACHE_LINE_COUNT
    xor ebx, ebx

FifoSearchLoop:
    mov eax, DWORD PTR [esi + ebx * 4]
    cmp eax, currentValue
    je FifoHit
    inc ebx
    loop FifoSearchLoop
    jmp FifoMiss

FifoHit:
    inc hitCount
    mov edx, OFFSET hitLabel
    call WriteString
    jmp FifoComplete

FifoMiss:
    inc missCount
    mov edx, OFFSET missLabel
    call WriteString

    mov ecx, CACHE_LINE_COUNT
    xor ebx, ebx

FifoFindEmpty:
    cmp DWORD PTR [esi + ebx * 4], EMPTY_CACHE_LINE
    je FifoInsert
    inc ebx
    loop FifoFindEmpty

    ; The cache is full. Replace the line selected by the FIFO cursor.
    mov ebx, fifoCursor
    inc fifoCursor
    mov eax, fifoCursor
    cmp eax, CACHE_LINE_COUNT
    jb FifoInsert
    mov fifoCursor, 0

FifoInsert:
    mov eax, currentValue
    mov DWORD PTR [esi + ebx * 4], eax

FifoComplete:
    popad
    ret
ApplyFifoPolicy ENDP

ApplyLruPolicy PROC
    pushad

    inc lruClock
    mov esi, OFFSET cacheLines
    mov ecx, CACHE_LINE_COUNT
    xor ebx, ebx

LruSearchLoop:
    mov eax, DWORD PTR [esi + ebx * 4]
    cmp eax, currentValue
    je LruHit
    inc ebx
    loop LruSearchLoop
    jmp LruMiss

LruHit:
    inc hitCount
    mov edx, OFFSET hitLabel
    call WriteString

    mov edi, OFFSET lruTimestamps
    mov eax, lruClock
    mov DWORD PTR [edi + ebx * 4], eax
    jmp LruComplete

LruMiss:
    inc missCount
    mov edx, OFFSET missLabel
    call WriteString

    mov esi, OFFSET cacheLines
    mov ecx, CACHE_LINE_COUNT
    xor ebx, ebx

LruFindEmpty:
    cmp DWORD PTR [esi + ebx * 4], EMPTY_CACHE_LINE
    je LruInsert
    inc ebx
    loop LruFindEmpty

    ; The cache is full. Find the line with the smallest timestamp.
    mov edi, OFFSET lruTimestamps
    mov ecx, CACHE_LINE_COUNT
    xor ebx, ebx
    xor edx, edx
    mov eax, 0FFFFFFFFh

LruVictimSearch:
    mov esi, DWORD PTR [edi + ebx * 4]
    cmp esi, eax
    jae LruNextCandidate
    mov eax, esi
    mov edx, ebx

LruNextCandidate:
    inc ebx
    loop LruVictimSearch
    mov ebx, edx

LruInsert:
    mov esi, OFFSET cacheLines
    mov eax, currentValue
    mov DWORD PTR [esi + ebx * 4], eax

    mov edi, OFFSET lruTimestamps
    mov eax, lruClock
    mov DWORD PTR [edi + ebx * 4], eax

LruComplete:
    popad
    ret
ApplyLruPolicy ENDP
