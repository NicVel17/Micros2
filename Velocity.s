.global _start

        ! Constants and data
dt:     .word   1              ! dt = 1 (simplified for integer math)
L:      .word   10             ! L = 10 (base distance between wheels)

        ! Array of wheel velocities (v_left, v_right) pairs as integers
vel_array:
        .word   10             ! v_left_1 = 1.0 * 10
        .word   10             ! v_right_1 = 1.0 * 10
        .word   10             ! v_left_2 = 1.0 * 10
        .word   20             ! v_right_2 = 2.0 * 10
        .word   20             ! v_left_3 = 2.0 * 10
        .word   10             ! v_right_3 = 1.0 * 10

array_size:
        .word   3               ! Number of velocity pairs

        ! Variables for calculations
x:      .word   0              ! Current x position
y:      .word   0              ! Current y position
theta:  .word   0              ! Current angle

        ! Output strings
pos_msg:        .ascii "Position: ("
x_msg:          .ascii ", "
y_msg:          .ascii ")\n",0
theta_msg:      .ascii "Theta: ",0
newline:        .ascii "\n",0
        .align 4

_start:
        ! Initialize registers
        sethi   %hi(vel_array), %l0
        or      %l0, %lo(vel_array), %l0
        
        sethi   %hi(array_size), %l1
        or      %l1, %lo(array_size), %l1
        ld      [%l1], %l1
        mov     0, %l2                  ! Initialize counter

loop:   
        ! Check if we're done
        cmp     %l2, %l1
        bge     done
        nop

        ! Load velocities for this iteration
        ld      [%l0], %o0              ! v_left
        ld      [%l0+4], %o1            ! v_right
        
        ! Calculate v = (v_left + v_right) / 2
        add     %o0, %o1, %o2           ! v_left + v_right
        srl     %o2, 1, %o4             ! Divide by 2 to get v

        ! Calculate omega = (v_right - v_left) / L
        sub     %o1, %o0, %o5           ! v_right - v_left
        sethi   %hi(L), %o6
        or      %o6, %lo(L), %o6
        ld      [%o6], %o6
        st      %o5, [%g0+IODevDivDL]   ! Store difference
        st      %o6, [%g0+IODevDivDiv]  ! Divide by L
        ld      [%g0+IODevDivSQ], %o7   ! Get omega

        ! Update theta (theta += omega * dt)
        sethi   %hi(dt), %l3
        or      %l3, %lo(dt), %l3
        ld      [%l3], %l3
        st      %o7, [%g0+IODevMulM1]   ! omega
        st      %l3, [%g0+IODevMulM2]   ! dt
        ld      [%g0+IODevMulSPL], %l4  ! Get omega * dt
        
        sethi   %hi(theta), %l5
        or      %l5, %lo(theta), %l5
        ld      [%l5], %l6
        add     %l6, %l4, %l6
        st      %l6, [%l5]              ! Store new theta

        ! Update x position (simplified for testing)
        sethi   %hi(x), %o0
        or      %o0, %lo(x), %o0
        ld      [%o0], %o1
        add     %o1, %o4, %o1           ! Add v to x directly for now
        st      %o1, [%o0]

        ! Update y position (simplified for testing)
        sethi   %hi(y), %o0
        or      %o0, %lo(y), %o0
        ld      [%o0], %o1
        add     %o1, %o4, %o1           ! Add v to y directly for now
        st      %o1, [%o0]

        ! Print position
        sethi   %hi(pos_msg), %o0
        or      %o0, %lo(pos_msg), %o0
        st      %o0, [%g0+IODevPrintStrz]
        
        sethi   %hi(x), %o0
        or      %o0, %lo(x), %o0
        ld      [%o0], %o1
        st      %o1, [%g0+IODevPrintInt]
        
        sethi   %hi(x_msg), %o0
        or      %o0, %lo(x_msg), %o0
        st      %o0, [%g0+IODevPrintStrz]
        
        sethi   %hi(y), %o0
        or      %o0, %lo(y), %o0
        ld      [%o0], %o1
        st      %o1, [%g0+IODevPrintInt]
        
        sethi   %hi(y_msg), %o0
        or      %o0, %lo(y_msg), %o0
        st      %o0, [%g0+IODevPrintStrz]

        ! Print theta for debugging
        sethi   %hi(theta_msg), %o0
        or      %o0, %lo(theta_msg), %o0
        st      %o0, [%g0+IODevPrintStrz]
        
        sethi   %hi(theta), %o0
        or      %o0, %lo(theta), %o0
        ld      [%o0], %o1
        st      %o1, [%g0+IODevPrintInt]
        
        sethi   %hi(newline), %o0
        or      %o0, %lo(newline), %o0
        st      %o0, [%g0+IODevPrintStrz]

        ! Increment counter and array pointer
        add     %l2, 1, %l2             ! Increment counter
        add     %l0, 8, %l0             ! Move to next velocity pair
        ba      loop
        nop

done:   
        ba      done
        nop