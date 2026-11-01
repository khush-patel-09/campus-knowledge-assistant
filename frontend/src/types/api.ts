
export interface AskRequest {
  question: string;
  department?: string | null;
  academic_year?: string | null;
  document_type?: string | null;
}

export interface Source {
  reference: number;
  title: string;
  page_number: number | null;
  section_title: string | null;
  source_url: string | null;
}

export interface AskResponse {
  answer: string;
  sources: Source[];
}
