import sympy
from sympy import symbols, sin, cos, tan, sec, Matrix, exp, I, simplify, pi, acos, conjugate

def solve_questions():
    print("--- Question 1: Perceived Euler Angle Rates ---")
    phi, theta, psi, q_mal = symbols('phi theta psi q_malicious')
    # Standard Inverse Jacobian (W) for ZYX convention
    W = Matrix([
        [1, sin(phi)*tan(theta), cos(phi)*tan(theta)],
        [0, cos(phi),           -sin(phi)],
        [0, sin(phi)*sec(theta), cos(phi)*sec(theta)]
    ])
    omega_spoofed = Matrix([0, q_mal, 0])
    euler_rates = W * omega_spoofed
    print(f"Phi_dot: {simplify(euler_rates[0])}")
    print(f"Theta_dot: {simplify(euler_rates[1])}")
    print(f"Psi_dot: {simplify(euler_rates[2])}")

    print("\n--- Question 2: Gimbal Lock Critical Angle ---")
    # Singularities in W occur when cos(theta) = 0
    # theta = pi/2 (90 degrees)
    det_J = cos(theta) 
    print(f"Determinant of forward Jacobian J: {det_J}")
    print("Singularity exists when det(J) = 0, which occurs at theta = pi/2 (90 degrees).")

    print("\n--- Question 3: Tampered Rotation Matrix Determinant ---")
    theta_rot = symbols('theta')
    # Valid rotation around k-axis (z-axis)
    R_valid = Matrix([
        [cos(theta_rot), -sin(theta_rot), 0],
        [sin(theta_rot), cos(theta_rot), 0],
        [0, 0, 1]
    ])
    print(f"Valid R Det: {R_valid.det()}")
    
    # Tampered: element [0,1] changed from -sin(theta) to 0 (or sin(theta) to 0)
    # The prompt says "from sin theta to 0". This might refer to a different convention.
    # If [0,1] is sin(theta), the matrix would be:
    R_init = Matrix([
        [cos(theta_rot), sin(theta_rot), 0], # Note: this is Ry or Rz transposed
        [-sin(theta_rot), cos(theta_rot), 0],
        [0, 0, 1]
    ])
    R_tampered = R_init.copy()
    R_tampered[0,1] = 0
    print(f"Tampered R Det: {simplify(R_tampered.det())}")

    print("\n--- Question 4: Quaternion Manipulation ---")
    # q = qr + qv = cos(theta/2) + sin(theta/2)u
    # Attack: qr -> -qr
    # q_new = -qr + qv = -cos(theta/2) + sin(theta/2)u
    # Using trig identity: cos(pi - theta/2) = -cos(theta/2)
    # And sin(pi - theta/2) = sin(theta/2)
    # So q_new = cos(pi - theta/2) + sin(pi - theta/2)u
    # Angle theta_new = 2 * (pi - theta/2) = 2pi - theta
    print("New rotation angle: 2*pi - theta (equivalent to -theta)")

    print("\n--- Question 5: NED to Vehicle Frame ---")
    # NED Frame: North (i), East (j), Down (k)
    # Rotation around j (East) by 60 degrees.
    y_rot = symbols('y_rot')
    Ry = Matrix([
        [cos(y_rot), 0, sin(y_rot)],
        [0, 1, 0],
        [-sin(y_rot), 0, cos(y_rot)]
    ])
    n, e, d = symbols('n e d')
    pv1 = Matrix([n, e, d])
    result = Ry.subs(y_rot, pi/3) * pv1
    print(f"pv2: {simplify(result)}")

    print("\n--- Question 6: 2D Complex Rotations ---")
    t1, t2 = symbols('theta1 theta2')
    z1 = exp(I*t1)
    z2 = exp(I*t2)
    z_res = z1 * z2
    print(f"Final orientation z1*z2: {z_res}")
    print("Property: Exponentials add, meaning rotations are additive.")

    print("\n--- Question 7: Body Angular Velocity from Malicious Yaw Rate ---")
    psi_mal = symbols('psi_malicious')
    # Kinematic Jacobian J (Maps euler rates to p,q,r)
    J = Matrix([
        [1, 0, -sin(theta)],
        [0, cos(phi), sin(phi)*cos(theta)],
        [0, -sin(phi), cos(phi)*cos(theta)]
    ])
    mal_rates = Matrix([0, 0, psi_mal])
    body_vel = simplify(J * mal_rates)
    print(f"p: {body_vel[0]}")
    print(f"q: {body_vel[1]}")
    print(f"r: {body_vel[2]}")

    print("\n--- Question 8: Wind Scaling Inner Product ---")
    r_val, k_val, th_val = symbols('r k theta')
    v_spoofed = Matrix([k_val*r_val*cos(th_val), k_val*r_val*sin(th_val)])
    i_unit = Matrix([1, 0])
    print(f"Inner product (x-component): {v_spoofed.dot(i_unit)}")

    print("\n--- Question 9: Effect of Negated Roll Gyro ---")
    p_true = symbols('p')
    # p_spoofed = -p_true, q=0, r=0
    omega_sp = Matrix([-p_true, 0, 0])
    euler_r = W * omega_sp
    print(f"Perceived phi_dot: {euler_r[0]}")

    print("\n--- Question 10: Opposite Quaternion Rotation ---")
    # p_mal = q^-1 p q
    # Contrast with p' = q p q^-1
    # q^-1 is often denoted q* for unit quaternions.
    # q^-1 = cos(-theta/2) + sin(-theta/2)u
    # So q^-1 p q rotates by -theta.
    print("Transformation q^-1 p q is mathematically equivalent to rotating p by -theta.")

if __name__ == "__main__":
    solve_questions()
