import * as yup from 'yup'
import { SUPPORTED_DB_TYPES } from './connectDB'

const portField = yup
  .number()
  .transform((v, o) => (o === '' || o == null ? undefined : v))
  .typeError('Port must be a number')
  .integer()
  .min(1)
  .max(65535)

const schema = yup.object({
  name: yup
    .string()
    .trim()
    .max(80, 'Connection name must be 80 characters or less')
    .required('Connection name is required'),
  db_type: yup
    .string()
    .oneOf(SUPPORTED_DB_TYPES, 'Unsupported database type')
    .required('Database type is required'),
  host: yup.string().when('db_type', {
    is: (t) => t !== 'sqlite',
    then: (f) => f.required('Host is required for remote databases'),
    otherwise: (f) => f.optional(),
  }),
  port: portField.when('db_type', {
    is: (t) => t !== 'sqlite',
    then: (f) => f.required('Port is required for remote databases'),
    otherwise: (f) => f.optional(),
  }),
  db_name: yup.string().when('db_type', {
    is: (t) => t === 'sqlite',
    then: (f) => f.required('Database path is required for SQLite'),
    otherwise: (f) => f.required('Database name is required'),
  }),
  username: yup.string().when('db_type', {
    is: (t) => t !== 'sqlite',
    then: (f) => f.required('Username is required'),
    otherwise: (f) => f.optional(),
  }),
  password: yup.string().when('db_type', {
    is: (t) => t !== 'sqlite',
    then: (f) => f.required('Password is required'),
    otherwise: (f) => f.optional(),
  }),
  ssl: yup.boolean().default(false),
}).required()

export default schema
