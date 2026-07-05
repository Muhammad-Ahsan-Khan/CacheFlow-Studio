; ============================================================================
; CacheFlow Studio - Console rendering procedures
; ============================================================================

RenderWelcomeScreen PROC
    mov edx, OFFSET brandBanner
    call WriteString
    mov edx, OFFSET menuFifo
    call WriteString
    mov edx, OFFSET menuLru
    call WriteString
    mov edx, OFFSET menuPrompt
    call WriteString
    ret
RenderWelcomeScreen ENDP

CapturePolicyChoice PROC
    call ReadDec
    mov activePolicy, eax

    cmp eax, POLICY_FIFO
    je PolicyAccepted
    cmp eax, POLICY_LRU
    je PolicyAccepted

    mov activePolicy, POLICY_FIFO
    mov edx, OFFSET invalidChoice
    call WriteString

PolicyAccepted:
    mov edx, OFFSET activeLabel
    call WriteString
    cmp activePolicy, POLICY_LRU
    je RenderLruName

    mov edx, OFFSET fifoLabel
    jmp RenderPolicyName

RenderLruName:
    mov edx, OFFSET lruLabel

RenderPolicyName:
    call WriteString
    call Crlf
    ret
CapturePolicyChoice ENDP

RenderSimulationHeader PROC
    mov edx, OFFSET runHeader
    call WriteString
    ret
RenderSimulationHeader ENDP

RenderStepDivider PROC
    mov edx, OFFSET stepDivider
    call WriteString
    ret
RenderStepDivider ENDP

RenderCurrentRequest PROC
    mov edx, OFFSET requestLabel
    call WriteString
    mov eax, currentIndex
    call WriteDec

    mov edx, OFFSET valueLabel
    call WriteString
    mov eax, currentValue
    call WriteDec
    ret
RenderCurrentRequest ENDP

RenderSearchMessage PROC
    mov edx, OFFSET searchLabel
    call WriteString
    ret
RenderSearchMessage ENDP

RenderCacheSnapshot PROC
    pushad

    mov edx, OFFSET cacheLabel
    call WriteString
    mov esi, OFFSET cacheLines
    mov ecx, CACHE_LINE_COUNT
    xor ebx, ebx

CacheRenderLoop:
    cmp ebx, 0
    je RenderCacheValue
    mov edx, OFFSET separator
    call WriteString

RenderCacheValue:
    mov eax, DWORD PTR [esi + ebx * 4]
    cmp eax, EMPTY_CACHE_LINE
    je RenderEmptyLine
    call WriteDec
    jmp RenderNextLine

RenderEmptyLine:
    mov edx, OFFSET emptyLabel
    call WriteString

RenderNextLine:
    inc ebx
    loop CacheRenderLoop

    mov edx, OFFSET cacheClose
    call WriteString
    popad
    ret
RenderCacheSnapshot ENDP

RenderFinalReport PROC
    mov edx, OFFSET summaryHeader
    call WriteString

    mov edx, OFFSET summaryHits
    call WriteString
    mov eax, hitCount
    call WriteDec
    call Crlf

    mov edx, OFFSET summaryMisses
    call WriteString
    mov eax, missCount
    call WriteDec
    call Crlf

    mov edx, OFFSET summaryTotal
    call WriteString
    mov eax, completedRequests
    call WriteDec
    call Crlf

    mov edx, OFFSET summaryRatio
    call WriteString

    cmp completedRequests, 0
    je RenderZeroRatio

    mov eax, hitCount
    mov ebx, 10000
    mul ebx
    mov ebx, completedRequests
    div ebx

    xor edx, edx
    mov ebx, 100
    div ebx
    mov ratioDecimals, edx
    call WriteDec

    mov al, '.'
    call WriteChar
    mov eax, ratioDecimals
    cmp eax, 10
    jae RenderRatioDecimals
    mov al, '0'
    call WriteChar
    mov eax, ratioDecimals

RenderRatioDecimals:
    call WriteDec
    jmp RenderPercentSign

RenderZeroRatio:
    mov eax, 0
    call WriteDec
    mov al, '.'
    call WriteChar
    mov al, '0'
    call WriteChar
    call WriteChar

RenderPercentSign:
    mov edx, OFFSET percentLabel
    call WriteString
    call Crlf
    call Crlf
    ret
RenderFinalReport ENDP
