export class Task {
    id: string;
    accountId: string;
    title: string;
    description: string;
    active: boolean;
    createdAt: string;
    updatedAt: string;

    constructor(json: any) {
        this.id = json.id;
        this.accountId = json.account_id;
        this.title = json.title;
        this.description = json.description;
        this.active = json.active;
        this.createdAt = json.created_at;
        this.updatedAt = json.updated_at;
    }
}
