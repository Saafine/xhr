export const testData = [
  {
    args: ['00-44  48 5555 8361'],
    output: '004-448-555-583-61'
  },
  {
    args: ['0 - 22 1985--324'],
    output: '022-198-53-24'
  },
  {
    args: ['555372654'],
    output: '555-372-654'
  }
];

export function solution(str) {
  const numbersStr = str.replace(/[^0-9]/g, '');
  const numSplit = numbersStr.length % 3;

  let doubleDigits;
  if (numSplit === 1) doubleDigits = 2;
  if (numSplit === 2) doubleDigits = 1;

  const doublePart = doubleSplit(numbersStr, doubleDigits);
  const triplePart =
    (!doubleDigits ?
      numbersStr.match(/.{1,3}/g) :
      numbersStr.slice(0, -2 * doubleDigits).match(/.{1,3}/g)) || [];

  return triplePart.concat(doublePart).join('-');
}

function doubleSplit(str, timesToSplit) {
  if (!timesToSplit) return [];
  return str.slice(-2 * timesToSplit).match(/.{1,2}/g) || [];
}

// trySolution(solution, testData);

// Alternative solutions
// --------------------
export function solution(str) {
  const numbers = str.split('').filter(part => /[0-9]/.exec(part));
  const numbersLen = numbers.length;
  const numberGrouped = numbersLen % 3;

  let type;
  if (numberGrouped === 0) { // grouped by 3
    type = 1;
  } else if (numberGrouped === 1) { // 2 groups by 2 at the end
    type = 3;
  } else { // 1 group of 2 at the end
    type = 2
  }

  let x = numbersLen -  1;
  let timeToDash = 0;
  while (x > 0) {
    if (type === 1) {
      if (timeToDash === 2) {
        numbers.splice(x, 0, '-');
        timeToDash = 0;
      } else {
        timeToDash++;
      }
    }

    if (type === 2) {
      if (x === numbersLen - 2) {
        numbers.splice(x, 0, '-');
        type = 1;
        // timeToDash = 0;
      }
    }

    if (type === 3) {
      if (x === numbersLen - 2 || x === numbersLen - 4) {
        numbers.splice(x, 0, '-');
        type = timeToDash === 1 ? 3 : 1;
        timeToDash = 1; // refactor
      }
    }

    x--;
  }

  return numbers.join('');
}
