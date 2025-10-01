

export interface EvaluationResponse {
    id?: number;
    assignmentId?: number;
    criteriaId?: number;
    score?: number;
    comments?: string;
    createdAt?: string;
    updatedAt?: string;
}


export interface EvaluationUI {
    id: number;
    assignmentId: number;
    criteriaId: number;
    score: number;
    comments: string;
    createdAt: string;
    updatedAt: string;
}
