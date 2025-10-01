

export interface AssignmentResponse {
    id?: number;
    eventId?: number;
    submissionId?: number;
    evaluatorId?: number;
    assignedAt?: string;
}


export interface AssignmentUI {
    id: number;
    eventId: number;
    submissionId: number;
    evaluatorId: number;
    assignedAt: string;
}
