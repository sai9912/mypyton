export function serverValidation(field) {
  return function () {
    return !this.serverErrors || !this.serverErrors[field]
  }
}
