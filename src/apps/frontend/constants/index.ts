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
  PASSWORD_MATCH_VALIDATION_ERROR:
    "The confirmed password doesn't match the chosen password.",
  PASSWORD_MIN_LENGTH: 8,
  PASSWORD_VALIDATION_ERROR: 'Please enter at least 8 characters long password',
  PHONE_NUMBER_BASED_AUTHENTICATION: 'PHONE',
  PHONE_VALIDATION_ERROR: 'Please enter a valid phone number',
  SEND_OTP_DELAY_IN_MS: 60_000,
  TOASTER_AUTO_HIDE_DURATION: 3000,
};

export default constant;
