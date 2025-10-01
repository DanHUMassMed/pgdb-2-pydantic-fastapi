

export interface CoordinatorResponse {
    id?: number;
    eventId?: number;
    firstName?: string;
    lastName?: string;
    email?: string;
    phone?: string;
    titleRole?: string;
    expertiseDescription?: string;
    affiliation?: string;
    status?: string;
    acceptedInviteToken?: string;
    acceptedInviteDate?: string;
    acceptedInvite?: boolean;
    createdAt?: string;
    updatedAt?: string;
}


export interface CoordinatorUI {
    id: number;
    eventId: number;
    firstName: string;
    lastName: string;
    email: string;
    phone: string;
    titleRole: string;
    expertiseDescription: string;
    affiliation: string;
    status: string;
    acceptedInviteToken: string;
    acceptedInviteDate: string;
    acceptedInvite: boolean;
    createdAt: string;
    updatedAt: string;
}
