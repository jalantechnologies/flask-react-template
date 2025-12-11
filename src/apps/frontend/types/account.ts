import { PhoneNumber } from 'frontend/types/auth';
import { JsonObject, Nullable } from 'frontend/types/common-types';

export class Account {
  id: string;
  firstName: string;
  lastName: string;
  phoneNumber: Nullable<PhoneNumber>;
  username: string;

  constructor(json: JsonObject) {
    this.id = json.id as string;
    this.firstName = json.first_name as string;
    this.lastName = json.last_name as string;
    this.phoneNumber = json.phone_number
      ? new PhoneNumber(json.phone_number as JsonObject)
      : null;
    this.username = json.username as string;
  }

  displayName(): string {
    const firstName = this.firstName || '';
    const lastName = this.lastName || '';
    const fullName = `${firstName} ${lastName}`.trim();
    
    // If no name is available, fallback to username
    return fullName || this.username || 'User';
  }
}
