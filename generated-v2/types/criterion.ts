

export interface CriterionResponse {
    id?: number;
    eventId?: number;
    label?: string;
    description?: string;
    category?: string;
    required?: boolean;
    sortPos?: number;
    weight?: number;
    maxRatingValue?: number;
    valueDescriptors?: string;
    createdAt?: string;
    updatedAt?: string;
}


export interface CriterionUI {
    id: number;
    eventId: number;
    label: string;
    description: string;
    category: string;
    required: boolean;
    sortPos: number;
    weight: number;
    maxRatingValue: number;
    valueDescriptors: string;
    createdAt: string;
    updatedAt: string;
}
