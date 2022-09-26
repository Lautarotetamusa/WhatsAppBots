xvfb=$(pgrep Xvfb)

if [ -z "$xvfb" ]; then
  Xvfb :10 -ac -screen 0 1024x768x8 &
  echo "ejecutando Xvfb $!"
else
  echo "Xvfb ya esta ejecutandose"
fi
