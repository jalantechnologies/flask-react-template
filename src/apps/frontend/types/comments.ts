export interface Comment {
  id: string;
  text: string;
  created_at: string;
  updated_at?: string;
}

export interface CreateCommentDto {
  text: string;
}

export interface UpdateCommentDto {
  text: string;
}
