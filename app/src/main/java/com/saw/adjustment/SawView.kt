package com.saw.adjustment

import android.content.Context
import android.graphics.Canvas
import android.graphics.Color
import android.graphics.DashPathEffect
import android.graphics.Paint
import android.graphics.RectF
import android.util.AttributeSet
import android.view.View
import kotlin.math.min

/**
 * Custom View that draws the saw centering visualization.
 *
 * World coordinate system:
 *   - Part tip at origin (0, 0).
 *   - Part rectangle: (-partRadius, 0) to (+partRadius, 1.0).
 *   - Positive Y points UP in world space (flipped to screen).
 *
 * Drawing elements (when saw result is present):
 *   - Part rectangle (bronze)
 *   - Saw circle (filled gray)
 *   - Two construction circles (dashed blue)
 *   - Green dots at construction circle centers
 *   - Red dots at intersection points
 *   - Vertical red line from saw center to saw center + radius
 */
class SawView @JvmOverloads constructor(
    context: Context,
    attrs: AttributeSet? = null,
    defStyleAttr: Int = 0
) : View(context, attrs, defStyleAttr) {

    // Input parameters (inches)
    var partDiameter: Double = 0.0
        private set
    var sawDiameter: Double = 0.0
        private set
    var rearSlotDepth: Double = 0.0
        private set
    var frontSlotDepth: Double = 0.0
        private set

    // Computed result (null = not yet computed or invalid)
    var sawResult: SawResult? = null
        private set

    // Whether we have valid part data to draw
    private var hasPartData = false

    // Whether we have full saw data to draw
    private var hasSawData = false

    // Error message to display instead of drawing
    var errorMessage: String? = null
        private set

    // World-to-screen transform
    private var scale = 1.0f
    private var offsetX = 0.0f
    private var offsetY = 0.0f

    // ---- Paints ----

    private val backgroundPaint = Paint().apply {
        color = Color.parseColor("#1A1A2E")
        style = Paint.Style.FILL
    }

    private val partPaint = Paint(Paint.ANTI_ALIAS_FLAG).apply {
        color = Color.parseColor("#CD7F32") // bronze
        style = Paint.Style.FILL
    }

    private val partStrokePaint = Paint(Paint.ANTI_ALIAS_FLAG).apply {
        color = Color.parseColor("#E8A850")
        style = Paint.Style.STROKE
        strokeWidth = 2f
    }

    private val sawFillPaint = Paint(Paint.ANTI_ALIAS_FLAG).apply {
        color = Color.parseColor("#888888")
        style = Paint.Style.FILL
        alpha = 140
    }

    private val sawStrokePaint = Paint(Paint.ANTI_ALIAS_FLAG).apply {
        color = Color.parseColor("#AAAAAA")
        style = Paint.Style.STROKE
        strokeWidth = 2f
    }

    private val constructionPaint = Paint(Paint.ANTI_ALIAS_FLAG).apply {
        color = Color.parseColor("#4488FF")
        style = Paint.Style.STROKE
        strokeWidth = 2f
        pathEffect = DashPathEffect(floatArrayOf(10f, 8f), 0f)
    }

    private val greenDotPaint = Paint(Paint.ANTI_ALIAS_FLAG).apply {
        color = Color.parseColor("#00CC00")
        style = Paint.Style.FILL
    }

    private val redDotPaint = Paint(Paint.ANTI_ALIAS_FLAG).apply {
        color = Color.parseColor("#FF0000")
        style = Paint.Style.FILL
    }

    private val redLinePaint = Paint(Paint.ANTI_ALIAS_FLAG).apply {
        color = Color.parseColor("#FF0000")
        style = Paint.Style.STROKE
        strokeWidth = 3f
    }

    private val axisPaint = Paint(Paint.ANTI_ALIAS_FLAG).apply {
        color = Color.parseColor("#444466")
        style = Paint.Style.STROKE
        strokeWidth = 1f
        pathEffect = DashPathEffect(floatArrayOf(6f, 6f), 0f)
    }

    private val errorTextPaint = Paint(Paint.ANTI_ALIAS_FLAG).apply {
        color = Color.parseColor("#FF6666")
        textSize = 40f
        textAlign = Paint.Align.CENTER
    }

    // ---- Public API ----

    /** Milestone 1: set only the part diameter and draw the part rectangle. */
    fun setPartOnly(partDiameter: Double) {
        this.partDiameter = partDiameter
        this.sawDiameter = 0.0
        this.rearSlotDepth = 0.0
        this.frontSlotDepth = 0.0
        this.sawResult = null
        this.hasPartData = partDiameter > 0.0
        this.hasSawData = false
        this.errorMessage = null
        invalidate()
    }

    /** Milestone 2: set all parameters, compute geometry, and draw everything. */
    fun setFullData(
        partDiameter: Double,
        sawDiameter: Double,
        rearSlotDepth: Double,
        frontSlotDepth: Double
    ) {
        this.partDiameter = partDiameter
        this.sawDiameter = sawDiameter
        this.rearSlotDepth = rearSlotDepth
        this.frontSlotDepth = frontSlotDepth
        this.hasPartData = partDiameter > 0.0
        this.errorMessage = null

        if (partDiameter <= 0.0 || sawDiameter <= 0.0) {
            this.sawResult = null
            this.hasSawData = false
            invalidate()
            return
        }

        val result = SawGeometry.computeSawCenter(
            partDiameter, sawDiameter, rearSlotDepth, frontSlotDepth
        )
        if (result == null) {
            this.sawResult = null
            this.hasSawData = false
            this.errorMessage = "No intersections found"
        } else {
            this.sawResult = result
            this.hasSawData = true
        }
        invalidate()
    }

    // ---- Drawing ----

    override fun onDraw(canvas: Canvas) {
        super.onDraw(canvas)
        canvas.drawRect(0f, 0f, width.toFloat(), height.toFloat(), backgroundPaint)

        if (!hasPartData) {
            errorTextPaint.textSize = 36f
            canvas.drawText(
                "Enter values and press Calculate",
                width / 2f, height / 2f, errorTextPaint
            )
            return
        }

        computeTransform()

        // Draw subtle axis lines through origin
        val originSx = worldToScreenX(0.0)
        val originSy = worldToScreenY(0.0)
        canvas.drawLine(0f, originSy, width.toFloat(), originSy, axisPaint)
        canvas.drawLine(originSx, 0f, originSx, height.toFloat(), axisPaint)

        // Draw saw circle (behind part)
        if (hasSawData) {
            drawSawCircle(canvas)
        }

        // Draw part rectangle (always on top of saw)
        drawPartRect(canvas)

        // Draw construction circles + dots + lines
        if (hasSawData) {
            drawConstructionCircles(canvas)
            drawDots(canvas)
            drawSawCenterLine(canvas)
        }

        // Draw error message if any
        errorMessage?.let {
            errorTextPaint.textSize = 36f
            canvas.drawText(it, width / 2f, 40f, errorTextPaint)
        }
    }

    /** Compute scale and offset so the world bounding box fits in the view with padding. */
    private fun computeTransform() {
        val partRadius = partDiameter / 2.0
        val sawRadius = sawDiameter / 2.0

        // Determine world bounding box
        var minX = -partRadius - 0.2
        var maxX = partRadius + 0.2
        var minY = -0.2
        var maxY = 1.2

        if (hasSawData && sawResult != null) {
            val sr = sawResult!!
            minX = minOf(minX, sr.sawCenterX - sawRadius - 0.2, -partRadius - sawRadius - 0.2)
            maxX = maxOf(maxX, sr.sawCenterX + sawRadius + 0.2, partRadius + sawRadius + 0.2)
            minY = minOf(minY, sr.sawCenterY - sawRadius - 0.2)
            maxY = maxOf(maxY, sr.sawCenterY + sawRadius + 0.2)
        }

        val worldW = maxX - minX
        val worldH = maxY - minY

        val padding = 40f
        val viewW = width - 2 * padding
        val viewH = height - 2 * padding

        // Uniform scale (no stretching), flip Y
        scale = min(viewW / worldW.toFloat(), viewH / worldH.toFloat())

        // Center the world bounding box in the view
        val worldCenterX = ((minX + maxX) / 2.0).toFloat()
        val worldCenterY = ((minY + maxY) / 2.0).toFloat()
        offsetX = width / 2f - worldCenterX * scale
        offsetY = height / 2f + worldCenterY * scale // +Y because screen Y is flipped
    }

    private fun worldToScreenX(wx: Double): Float = (wx.toFloat() * scale + offsetX)
    private fun worldToScreenY(wy: Double): Float = (-wy.toFloat() * scale + offsetY) // flip Y

    private fun drawPartRect(canvas: Canvas) {
        val partRadius = partDiameter / 2.0
        val left = worldToScreenX(-partRadius)
        val top = worldToScreenY(1.0)    // top of part in world = y=1
        val right = worldToScreenX(partRadius)
        val bottom = worldToScreenY(0.0)  // bottom of part in world = y=0
        val rect = RectF(left, top, right, bottom)
        canvas.drawRect(rect, partPaint)
        canvas.drawRect(rect, partStrokePaint)
    }

    private fun drawSawCircle(canvas: Canvas) {
        val sr = sawResult ?: return
        val sawRadius = sawDiameter / 2.0
        val cx = worldToScreenX(sr.sawCenterX)
        val cy = worldToScreenY(sr.sawCenterY)
        val r = (sawRadius * scale).toFloat()
        canvas.drawCircle(cx, cy, r, sawFillPaint)
        canvas.drawCircle(cx, cy, r, sawStrokePaint)
    }

    private fun drawConstructionCircles(canvas: Canvas) {
        val partRadius = partDiameter / 2.0
        val sawRadius = sawDiameter / 2.0
        val r = (sawRadius * scale).toFloat()

        // Circle 1: center (-partRadius, rearSlotDepth)
        val c1x = worldToScreenX(-partRadius)
        val c1y = worldToScreenY(rearSlotDepth)
        canvas.drawCircle(c1x, c1y, r, constructionPaint)

        // Circle 2: center (+partRadius, frontSlotDepth)
        val c2x = worldToScreenX(partRadius)
        val c2y = worldToScreenY(frontSlotDepth)
        canvas.drawCircle(c2x, c2y, r, constructionPaint)
    }

    private fun drawDots(canvas: Canvas) {
        val partRadius = partDiameter / 2.0
        val dotRadius = 8f

        // Green dots at construction circle centers
        canvas.drawCircle(
            worldToScreenX(-partRadius),
            worldToScreenY(rearSlotDepth),
            dotRadius, greenDotPaint
        )
        canvas.drawCircle(
            worldToScreenX(partRadius),
            worldToScreenY(frontSlotDepth),
            dotRadius, greenDotPaint
        )

        // Red dots at intersection points
        val sr = sawResult ?: return
        canvas.drawCircle(
            worldToScreenX(sr.intersectionA.first),
            worldToScreenY(sr.intersectionA.second),
            dotRadius, redDotPaint
        )
        canvas.drawCircle(
            worldToScreenX(sr.intersectionB.first),
            worldToScreenY(sr.intersectionB.second),
            dotRadius, redDotPaint
        )
    }

    private fun drawSawCenterLine(canvas: Canvas) {
        val sr = sawResult ?: return
        val sawRadius = sawDiameter / 2.0
        val x1 = worldToScreenX(sr.sawCenterX)
        val y1 = worldToScreenY(sr.sawCenterY)
        val y2 = worldToScreenY(sr.sawCenterY + sawRadius)
        canvas.drawLine(x1, y1, x1, y2, redLinePaint)
    }
}
