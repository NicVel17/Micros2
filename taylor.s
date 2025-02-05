.global _start

! Constants and data

x:      .word   2               ! Value of x to calculate e^x for

terms:  .word   5               ! Number of terms to use in Taylor series

result: .word   0               ! Will store final result

! Output strings

msg1:   .ascii  "Calculating e^"

msg2:   .ascii  " using Taylor series\n",0

msg3:   .ascii  "Result = "

msg4:   .ascii  "\n",0

        .align 4

_start:

        ! Initialize registers

        mov     1, %l0                  ! Current term value

        mov     1, %l1                  ! Final sum

        mov     1, %l2                  ! Current factorial

        mov     1, %l3                  ! Current power of x

        

        ! Load x value

        sethi   %hi(x), %g1

        or      %g1, %lo(x), %g1

        ld      [%g1], %l4             ! x value in %l4

        

        ! Load number of terms

        sethi   %hi(terms), %g1

        or      %g1, %lo(terms), %g1

        ld      [%g1], %l5             ! terms in %l5

        

        mov     0, %l6                  ! Counter starts at 0

        ! Print initial message

        sethi   %hi(msg1), %o0

        or      %o0, %lo(msg1), %o0

        st      %o0, [%g0+IODevPrintStrz]

        

        ! Print x value

        mov     %l4, %o0

        st      %o0, [%g0+IODevPrintInt]

        

        ! Print rest of message

        sethi   %hi(msg2), %o0

        or      %o0, %lo(msg2), %o0

        st      %o0, [%g0+IODevPrintStrz]

loop:   

        ! Check if we've calculated enough terms

        cmp     %l6, %l5

        bge     done

        nop

        ! If this is the first term (n=0), skip calculations

        cmp     %l6, 0

        be      add_term

        nop

        ! Calculate next power of x

        st      %l3, [%g0+IODevMulM1]   ! Current x^n

        st      %l4, [%g0+IODevMulM2]   ! x

        ld      [%g0+IODevMulSPL], %l3  ! New x^(n+1)

        ! Update factorial

        st      %l2, [%g0+IODevMulM1]   ! Current n!

        add     %l6, 1, %o0             ! n+1

        st      %o0, [%g0+IODevMulM2]   ! Multiply by next number

        ld      [%g0+IODevMulSPL], %l2  ! New (n+1)!

        ! Calculate term: x^n/n!

        st      %l3, [%g0+IODevDivDL]   ! x^n

        mov     0, %g1

        st      %g1, [%g0+IODevDivDH]   ! Clear high word

        st      %l2, [%g0+IODevDivDiv]  ! n!

        ld      [%g0+IODevDivSQ], %l7   ! Get term

add_term:

        ! Add to sum

        add     %l1, %l7, %l1           ! Add term to sum

        

        ! Increment counter

        add     %l6, 1, %l6

        ba      loop

        nop

done:   

        ! Store result

        sethi   %hi(result), %g1

        or      %g1, %lo(result), %g1

        st      %l1, [%g1]

        

        ! Print result message

        sethi   %hi(msg3), %o0

        or      %o0, %lo(msg3), %o0

        st      %o0, [%g0+IODevPrintStrz]

        

        ! Print result

        mov     %l1, %o0

        st      %o0, [%g0+IODevPrintInt]

        

        ! Print newline

        sethi   %hi(msg4), %o0

        or      %o0, %lo(msg4), %o0

        st      %o0, [%g0+IODevPrintStrz]

        

        ! Exit program

        ba      done                    ! Infinite loop at end

        nop