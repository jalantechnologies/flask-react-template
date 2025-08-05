interface Country {
  code: string;
  dialCode: string;
  flag: string;
  name: string;
}

const COUNTRIES: Country[] = [
  {
    code: 'US',
    dialCode: '+1',
    flag: '🇺🇸',
    name: 'United States',
  },
  {
    code: 'IN',
    dialCode: '+91',
    flag: '🇮🇳',
    name: 'India',
  },
];

const COUNTRY_SELECT_OPTIONS = COUNTRIES.map((country) => ({
  label: `${country.flag} ${country.code} (${country.dialCode})`,
  value: `${country.dialCode}, ${country.code}`,
}));

export default COUNTRY_SELECT_OPTIONS;
