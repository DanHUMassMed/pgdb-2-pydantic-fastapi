

export interface SubmissionResponse {
    id?: number;
    eventId?: number;
    participantId?: number;
    title?: string;
    shortDescription?: string;
    descriptionAbstract?: string;
    submissionCategory?: string;
    submissionSubCategory?: string;
    keywords?: string;
    externalLink?: string;
    submissionStatus?: string;
    createdAt?: string;
    updatedAt?: string;
}


export interface SubmissionUI {
    id: number;
    eventId: number;
    participantId: number;
    title: string;
    shortDescription: string;
    descriptionAbstract: string;
    submissionCategory: string;
    submissionSubCategory: string;
    keywords: string;
    externalLink: string;
    submissionStatus: string;
    createdAt: string;
    updatedAt: string;
}
