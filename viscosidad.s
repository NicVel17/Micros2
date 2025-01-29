suma_vect; !w=w+v
%i0 ! numero de elementos del vector
%i1 ! dirección de memoria del vector u
%i2 ! dirección de memoria del vector v
%i3 ! dirección de memoria del vector w

escala_vect: !w=ku
%i0 ! numero de elementos del vector
%i1 ! dirección de memorias del vector u
%i2 ! escalar k
%i3 ! dirección de memoria del vector w

Vector_sobre_escalar: !w=uk
%i0 ! numero de elementos 
%i1 ! dir de memoria del vector u
%i2 ! escalar k
%i3 ! direccion de memoria del vector w

acumula_pasos:
%i0 ! número de elementos de los vectores
%i1 ! direccion memoria Pos_i = Pos
%i2 ! dirección memoria V_i=V
%i3 ! escalar Kv
%i4 ! escalar paso
%i5 ! escalar t
%O0 ! numero de elementos del vector
%O1 ! numero de vectores retornados
%02 ! dirección de la memoria de la lista

sub %g0;%i3,%i3
mov %i4,%i0 !%i0 indice paso
mov %i1,i1% !Pos
mov %i2, %i2 ! Vel

loop:
	subcc %i0, 1, %i0
	be fin
	mov %i2, %i1
	mov %i3, %i2
	set ?, %i3 ! %i4 Fuerza
	Call escalar_vector
	NOP