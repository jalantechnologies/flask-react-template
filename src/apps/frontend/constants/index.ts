const passwordPolicy = {
  minLength: 8,
  lengthError: 'Please enter at least 8 characters long password',
  matchError: "The confirmed password doesn't match the chosen password.",
  strengthError:
    'Please choose a stronger password. Add length and avoid common words or predictable patterns.',
};

const constant = {
  DEFAULT_ERROR_HTTP_STATUS_CODE: 500,
  EMAIL_BASED_AUTHENTICATION: 'EMAIL',
  EMAIL_VALIDATION_ERROR: 'Please enter a valid email',
  FIRST_NAME_MIN_LENGTH: 1,
  FIRST_NAME_VALIDATION_ERROR: 'Please specify your first name',
  LAST_NAME_MIN_LENGTH: 1,
  LAST_NAME_VALIDATION_ERROR: 'Please specify your last name',
  OTP_INPUT_MAX_LENGTH: 2,
  OTP_LENGTH: 4,
  passwordPolicy,
  PHONE_NUMBER_BASED_AUTHENTICATION: 'PHONE',
  PHONE_VALIDATION_ERROR: 'Please enter a valid phone number',
  SEND_OTP_DELAY_IN_MS: 60_000,
  TOASTER_AUTO_HIDE_DURATION: 3000,
};

export default constant;
