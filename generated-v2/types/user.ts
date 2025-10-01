

export interface UserResponse {
    id?: number;
    firstName?: string;
    lastName?: string;
    email?: string;
    password?: string;
    organization?: string;
    isVerified?: boolean;
    magicLinkToken?: string;
    magicLinkExpiresAt?: string;
    registeredAt?: string;
    lastLoginAt?: string;
    role?: string;
}


export interface UserUI {
    id: number;
    firstName: string;
    lastName: string;
    email: string;
    password: string;
    organization: string;
    isVerified: boolean;
    magicLinkToken: string;
    magicLinkExpiresAt: string;
    registeredAt: string;
    lastLoginAt: string;
    role: string;
}
