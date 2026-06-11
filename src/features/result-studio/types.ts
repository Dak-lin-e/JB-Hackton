export type ResultTabId = 'concept' | 'production' | 'shorts' | 'cardNews' | 'risk' | 'abTest'

export interface ResultTab {
  id: ResultTabId
  label: string
}
