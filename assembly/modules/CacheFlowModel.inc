; ============================================================================
; CacheFlow Studio - Data model and constants
; ============================================================================

POLICY_FIFO          EQU 1
POLICY_LRU           EQU 2
MEMORY_WORD_COUNT    EQU 20
CACHE_LINE_COUNT     EQU 5
DEFAULT_REQUESTS     EQU 30
EMPTY_CACHE_LINE     EQU -1

.data

; Main memory keeps the original 20 values.
memoryWords DWORD 10,20,30,40,50,60,70,80,90,100
            DWORD 110,120,130,140,150,160,170,180,190,200

; Cache model.
cacheLines      DWORD CACHE_LINE_COUNT DUP(EMPTY_CACHE_LINE)
fifoCursor      DWORD 0
lruTimestamps   DWORD CACHE_LINE_COUNT DUP(0)
lruClock        DWORD 0
activePolicy    DWORD POLICY_FIFO

; Current request and run configuration.
configuredRequests DWORD DEFAULT_REQUESTS
currentIndex       DWORD 0
currentValue       DWORD 0

; Metrics.
hitCount          DWORD 0
missCount         DWORD 0
completedRequests DWORD 0
ratioDecimals     DWORD 0

; Console branding and messages.
brandBanner BYTE 0Dh,0Ah
            BYTE "============================================================================",0Dh,0Ah
            BYTE "||                         CACHEFLOW STUDIO                               ||",0Dh,0Ah
            BYTE "||                    Cache Policy Visual Simulator                       ||",0Dh,0Ah
            BYTE "============================================================================",0Dh,0Ah,0

menuFifo       BYTE "   1. FIFO  - First In, First Out",0Dh,0Ah,0
menuLru        BYTE "   2. LRU   - Least Recently Used",0Dh,0Ah,0
menuPrompt     BYTE 0Dh,0Ah,"   Select a replacement policy (1-2): ",0
invalidChoice BYTE 0Dh,0Ah,"   Invalid selection. FIFO has been selected.",0Dh,0Ah,0
activeLabel   BYTE 0Dh,0Ah,"   Active policy: ",0
fifoLabel     BYTE "FIFO",0
lruLabel      BYTE "LRU",0

runHeader BYTE 0Dh,0Ah
          BYTE "----------------------------------------------------------------------------",0Dh,0Ah
          BYTE "                         SIMULATION RUNNING",0Dh,0Ah
          BYTE "----------------------------------------------------------------------------",0Dh,0Ah,0

stepDivider BYTE 0Dh,0Ah,"----------------------------------------------------------------------------",0Dh,0Ah,0
requestLabel BYTE "CPU request  | memory index: ",0
valueLabel   BYTE "  | value: ",0
searchLabel  BYTE 0Dh,0Ah,"Searching the cache...",0
hitLabel     BYTE 0Dh,0Ah,"Result       | HIT  - value already exists in cache",0
missLabel    BYTE 0Dh,0Ah,"Result       | MISS - loading value from main memory",0
cacheLabel   BYTE 0Dh,0Ah,"Cache state  | [ ",0
separator    BYTE ", ",0
cacheClose   BYTE " ]",0Dh,0Ah,0
emptyLabel   BYTE "__",0

summaryHeader BYTE 0Dh,0Ah
              BYTE "============================================================================",0Dh,0Ah
              BYTE "                              FINAL REPORT",0Dh,0Ah
              BYTE "============================================================================",0Dh,0Ah,0
summaryHits   BYTE "   Cache hits:       ",0
summaryMisses BYTE "   Cache misses:     ",0
summaryTotal  BYTE "   Total requests:   ",0
summaryRatio  BYTE "   Hit ratio:        ",0
percentLabel  BYTE "%",0
